import requests
import pandas as pd
import numpy as np
from lxml import html
from bs4 import BeautifulSoup
import re
import datetime

from typing import List, Tuple
from bs4.element import Tag, ResultSet
from requests.sessions import Session

from dotenv import load_dotenv
load_dotenv()

import os
import sys
sys.path.append(os.getcwd())
import config


"""
START WEBCLIENT
"""

def start_webclient() -> Session:

    client = requests.session()
    client.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"})

    return client

client = start_webclient()   


def open_website_in_client(url:str) -> str:
    result = client.get(url)
    if result.status_code == 200:        
        return result.content.decode(result.encoding)
    else:
        raise ConnectionError


def find_all_links_in_table(soup: BeautifulSoup) -> List: 
    """Loop through all rows in a table and extract links from the fields."""
    links = []
    for tr in soup.findAll("tr"):
        trs = tr.findAll("td")
        for each in trs:
            try:
                link = each.find('a')['href']
                links.append(link)
            except:
                pass
    return links


def remove_duplicates_from_list(lst: list) -> list:
    """"Remove duplicates from list while maintaining the order"""
    return list(dict.fromkeys(lst))


def extract_url_by_class(html_string: str, level:str, class_str:str) -> List[str]:
    tree = html.fromstring(html_string)
    return tree.xpath(f'//{level}[@class="{class_str}"]/@href')


def extract_txt_by_class(html_string: str, level:str, class_str:str) -> List[str]:
    tree = html.fromstring(html_string)
    txt = tree.xpath(f'//{level}[@class="{class_str}"]/text()')
    txt_cleaned = [string.replace(' ', '').replace('\n', '').replace('\r', '') for string in txt]
    return list(filter(None, txt_cleaned))


def extract_txt_from_string(string:str, regex:str) -> str:
    result = re.search(regex, string)
    if result: return result.group(1)


def extract_clubs_from_html(url: str) -> pd.DataFrame:
    """Extract info from clubs table."""

    html_string = open_website_in_client(url)

    # Extract basic table
    result = pd.read_html(html_string)[0]
    result = result.iloc[:-2]['Team'].to_frame()  

    # Extract URLS
    soup = BeautifulSoup(html_string, 'html.parser')
    soup_clubs = soup.find_all('table', class_='leaguetable sortable table detailed-table')
    all_urls = find_all_links_in_table(soup_clubs[0])
    all_team_urls = [url for url in all_urls if 'teams' in url]
    result['SW_TeamURL'] = all_team_urls
    result['SW_Teamnaam'] = result['SW_TeamURL'].str.extract(config.REGEXES['team_name_from_url'], expand=True)
    result['SW_TeamID'] = result['SW_TeamURL'].str.extract(config.REGEXES['team_id_from_url'], expand=True).astype('int')
    
    return result


def determine_match_clusters(matches: pd.DataFrame) -> pd.DataFrame:
    """
    Determine the cluster a match belongs to.

    Rules: 
    - First (chronologically ordered) match is cluster 1
    - Match is of the same cluster as the previous match if there is 0 or 1 day in between  
    """

    matches['Datum'] = pd.to_datetime(matches['Datum'])
    matches = matches.sort_values(by='Datum').reset_index(drop=True)
    matches['Datum_Diff'] = (matches['Datum'] - matches.shift(1)['Datum']).dt.days.fillna(0)

    clusters = []
    for idx, row in matches.iterrows():
        if idx == 0: 
            clusters.append(1)
        elif row['Datum_Diff'] <= 1: 
            clusters.append(clusters[-1])
        else: clusters.append(clusters[-1]+1)
        
    matches['Cluster'] = clusters

    return matches


def extract_matches_from_html(url: str) -> pd.DataFrame:
    """Extract info from matches table."""

    html_string = open_website_in_client(url)

    # Extract basic table 
    result = pd.read_html(html_string)[0]
    result.columns = ['Datum', 'Competitie', 'Thuisteam', 'Uitslag', 'Uitteam', 'x1', 'x2']
    result['Datum'] = pd.to_datetime(result['Datum'], format='%d/%m/%y').dt.date

    # Extract URLS
    soup = BeautifulSoup(html_string, 'html.parser')
    soup_matches = soup.find_all('table', class_='matches')
    all_urls = find_all_links_in_table(soup_matches[0])
    all_urls_no_events = [url for url in all_urls if '#events' not in url]    
    chunk_size = 4
    urls_in_chunks = [all_urls_no_events[i:i+chunk_size] for i in range(0, len(all_urls_no_events), chunk_size)]    
    result[['x3', 'url_club_home', 'url_match', 'url_club_away']] = urls_in_chunks

    # Filter only Eredivisie
    result = result[result['Competitie'] == 'ERE']

    # Filter matches for only relevant season
    year = int(os.getenv('FOOTBALL_COMPETITION_YEAR'))
    begin = datetime.date(year, 7, 15)
    end = datetime.date(year+1, 6, 1)
    result = result[(result['Datum'] >= begin) & (result['Datum'] < end)]

    # Drop unnecessary columns
    result.drop(['x1', 'x2', 'x3'], axis=1, inplace=True)

    return result


def extract_squad_from_html(url: str) -> pd.DataFrame:
    """Extracts squad information from HTML."""
    
    html_string = open_website_in_client(url)

    # Basic table
    result = pd.read_html(html_string)[0]
    result_short = result[['Unnamed: 0', 'Naam', 'P']].rename({'Unnamed: 0':'Rugnummer', 'P':'Positie'}, axis=1)

    # Append with player links
    soup = BeautifulSoup(html_string, 'html.parser')
    soup_squad = soup.find_all('div', class_='squad-container')
    player_urls = remove_duplicates_from_list(find_all_links_in_table(soup_squad[0]))
    result_short['Link'] = player_urls[:-1] # Do not include the last person, the coach
    result_short['SW_Naam'] = result_short['Link'].str.extract(config.REGEXES['player_name_from_url'], expand=True)
    result_short['SW_ID'] = result_short['Link'].str.extract(config.REGEXES['player_id_from_url'], expand=True).astype('int')
    
    return result_short


def find_substitutions(subs_df: pd.DataFrame, base_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine DataFrame with substitutions with the DataFrame containing starting 11.
    Determine minutes played for each player.
    """

    subs_df_split = (subs_df['Speler'].str.split('([\w\s\.]+) for ([\w\s\.]+) ([0-9]+)\'', expand=True))
    all_subs = subs_df_split[1].fillna(subs_df_split[0]).rename('Speler')
    sub_minutes_played = 90-subs_df_split[3].fillna(90).astype('int').rename('Minuten_Gespeeld')
    subs_df2 = pd.concat([subs_df['#'], all_subs, subs_df['Link'], sub_minutes_played], axis=1)

    players_out = subs_df_split[2].rename('Speler')
    players_out_minutes_played = subs_df_split[3].fillna(90).astype('int').rename('Minuten_Gespeeld')
    players_out_df = pd.concat([players_out, players_out_minutes_played], axis=1).dropna()

    base_df = base_df.join(players_out_df.set_index('Speler'), on='Speler')
    base_df['Minuten_Gespeeld'].fillna(90, inplace=True)
    base_df['Minuten_Gespeeld'] = base_df['Minuten_Gespeeld'].astype('int')

    combined_lineup = pd.concat([base_df, subs_df2])
    return combined_lineup


def extract_lineup_from_html(soup_lineups: ResultSet, position:str) -> pd.DataFrame:
    """
    Extract the full team lineup from a BeautifulSoup Resultset. 
    Position indicates whether to process the left- or right container.
    """

    soup_lineup = soup_lineups[0].find('div', class_='container '+position)
    lineups = pd.read_html(str(soup_lineup))[0]
    lineups['Link'] = find_all_links_in_table(soup_lineup)

    soup_subs = soup_lineups[1].find('div', class_='container '+position)
    subs = pd.read_html(str(soup_subs))[0]
    subs['Link'] = find_all_links_in_table(soup_subs)

    full_lineup = find_substitutions(subs, lineups)
    full_lineup.reset_index(drop=True, inplace=True)

    # Drop the coach & Kaarten column
    full_lineup = full_lineup[~full_lineup['Speler'].str.contains('Coach:', regex=False)]
    full_lineup.drop(['Kaarten'], axis=1, inplace=True)

    full_lineup['SW_Naam'] = full_lineup['Link'].str.extract(config.REGEXES['player_name_from_url'], expand=True)
    full_lineup['SW_ID'] = full_lineup['Link'].str.extract(config.REGEXES['player_id_from_url'], expand=True).astype('int')

    return full_lineup
    

def extract_team_lineup(html_string: str) -> pd.DataFrame:
    """
    Extract the full team lineups and minutes played for home and away teams.
    Return as a single DataFrame with Home_Team as a boolean column to indicate which team played at home.
    """

    soup = BeautifulSoup(html_string, 'html.parser')
    soup_lineups = soup.find_all('div', class_='combined-lineups-container')

    full_lineup_home = extract_lineup_from_html(soup_lineups, 'left')
    full_lineup_away = extract_lineup_from_html(soup_lineups, 'right')
    full_lineup = (pd
                    .merge(full_lineup_home, full_lineup_away, how='outer', indicator='Home_Team')
                   .replace({'Home_Team':{'left_only':True, 'right_only':False}})
                  )

    return full_lineup.reset_index(drop=True)
    

def determine_assisters(html_string: str) -> List[str]:
    """Determine who assisted goals, return as a list containing the url's of the player pages."""

    soup = BeautifulSoup(html_string, 'html.parser')
    all_scorers_list = soup.find('ul', {'class':'scorer-info'}).findChildren('span', {'class':'scorer'})

    assister_urls = [] 

    for lineitem in all_scorers_list:
        for item in lineitem.contents:
            if type(item) == Tag:
                if 'assist' in str(item):
                    assister = re.findall('<a href="(.+?)">', str(item))
                    if assister: assister_urls.append(assister[0])
                        
    return assister_urls


def append_assisters(html_string: str, lineups: pd.DataFrame) -> pd.DataFrame:
    """Append the lineups with information on who assisted with goals."""
    
    # Starting state: no assists
    lineups['Assist'] = 0
    
    if any(lineups['Goal'] > 0):
        assisters = determine_assisters(html_string)
        for assister in assisters: lineups.loc[assister == lineups['Link'], 'Assist'] += 1 
        
    return lineups


def extract_match_events_from_lineup_container(
    html_string: str
    ) -> Tuple[List[str], List[str], List[str], List[str], List[str], List[str], List[int], List[int]]:
    """Extract important match events from the HTML, return as a tuple of lists"""

    def return_href_after_image_search(link_list: List[str], img_name: str, row: Tag, text: Tag):
        """Appends a list with the respective player href link."""
        
        result = re.findall(img_name, str(text))
        for _ in range(len(result)):
            link_list.append(row.find('td', {'class':'player large-link'}).a['href'])


    def return_minute_after_image_search(link_list: list[int], img_name: str, row: Tag, text: Tag):
        """Append a list with the minute a certain action is performed."""
        
        result = re.findall(f'.*{img_name}.+/> ([0-9]+)\'+', str(text))
        if result:
            link_list.append(int(result[0]))

    soup = BeautifulSoup(html_string, 'html.parser')
    soup_lineups = soup.find_all('div', class_='combined-lineups-container')
    
    # Pre-allocate empty lists
    cards_red = []
    cards_yellow = []
    goals_general = []
    goals_penalty = []
    goals_own = []
    penalty_missed = []
    minutes_red_card = []
    minutes_pen_mis = []

    for result in soup_lineups:
        rows = result.find_all('tr')
        for row in rows:
            for child in row.children:
                if type(child) == Tag:

                    return_href_after_image_search(cards_yellow, '/YC.png', row, child)
                    return_href_after_image_search(cards_red, '/Y2C.png', row, child)
                    return_href_after_image_search(cards_red, '/RC.png', row, child)
                    return_href_after_image_search(goals_general, '/G.png', row, child)
                    return_href_after_image_search(goals_penalty, '/PG.png', row, child)
                    return_href_after_image_search(goals_own, '/OG.png', row, child)
                    return_href_after_image_search(penalty_missed, '/PM.png', row, child)

                    return_minute_after_image_search(minutes_red_card, '/Y2C.png', row, child)
                    return_minute_after_image_search(minutes_red_card, '/RC.png', row, child)
                    return_minute_after_image_search(minutes_pen_mis, '/PM.png', row, child)
                    
    return cards_yellow, cards_red, goals_general, goals_penalty, goals_own, penalty_missed, minutes_red_card, minutes_pen_mis
    

def append_match_events(html_string: str, lineups: pd.DataFrame, dim_players: pd.DataFrame) -> pd.DataFrame:
    """Append the lineups with information on who took part in match events."""
    
    lineups[['Kaart_Geel', 'Kaart_Rood', 'Goal', 'Goal_Eigen', 'Penalty_Goal', 'Penalty_Gemist', 'Penalty_Gestopt']] = 0
    yc, rc, goals, goals_pen, goals_own, pen_mis, rc_min, pen_mis_min = extract_match_events_from_lineup_container(html_string)
    
    for player_href in yc: lineups.loc[player_href == lineups['Link'], 'Kaart_Geel'] += 1      
    for player_href in goals: lineups.loc[player_href == lineups['Link'], 'Goal'] += 1 
    for player_href in goals_own: lineups.loc[player_href == lineups['Link'], 'Goal_Eigen'] += 1 
    for player_href in goals_pen: lineups.loc[player_href == lineups['Link'], 'Penalty_Goal'] += 1 
    
    # Red Card has extra logic for minutes played
    for player_href, minutes in zip(rc, rc_min): 
        lineups.loc[player_href == lineups['Link'], 'Kaart_Rood'] += 1
        lineups.loc[player_href == lineups['Link'], 'Minuten_Gespeeld'] -= (90-minutes)

    # Penalty missed: extra logic to give active goalkeeper of opposition a +1 on PenaltyStopped
    for player_href, minutes in zip(pen_mis, pen_mis_min):
        lineups.loc[player_href == lineups['Link'], 'Penalty_Gemist'] += 1  

        # Find active opposition goalkeeper
        gk_team = ~lineups.loc[player_href == lineups['Link'], 'Home_Team'].unique()[0]
        lineups_with_pos = lineups.join(dim_players[['Link', 'Positie']].set_index('Link'))
        gk_mask = (lineups_with_pos['Positie']=='K') & (lineups_with_pos['Home_Team']==gk_team)
        for idx,gk in lineups_with_pos[gk_mask].iterrows():
            if gk['Minuten_Gespeeld'] == 90:
                lineups.iloc[idx]['Penalty_Gestopt'] += 1
            elif gk['Minuten_Gespeeld'] > pen_mis_min:
                lineups.iloc[idx]['Penalty_Gestopt'] += 1
            elif gk['Minuten_Gespeeld'] > 0:
                lineups.iloc[idx]['Penalty_Gestopt'] += 1
            else:
                pass

    return lineups


def determine_winning_team(score_home: int, score_away: int, lineups: pd.DataFrame) -> pd.DataFrame:
    """Fill Win/Loss/Draw columns in lineups"""

    # Pre-allocate values for columns Winst, Verlies and Gelijkspel
    lineups[['Wedstrijd_Gewonnen', 'Wedstrijd_Verloren', 'Wedstrijd_Gelijk']] = False

    if score_home > score_away:
        lineups.loc[lineups['Home_Team'], 'Wedstrijd_Gewonnen'] = True
        lineups.loc[~lineups['Home_Team'], 'Wedstrijd_Verloren'] = True
    elif score_away > score_home:
        lineups.loc[lineups['Home_Team'], 'Wedstrijd_Verloren'] = True
        lineups.loc[~lineups['Home_Team'], 'Wedstrijd_Gewonnen'] = True
    else:
        lineups['Wedstrijd_Gelijk'] = True
    
    return lineups


def determine_goals_against(lineups: pd.DataFrame, score_home: int, score_away: int) -> pd.DataFrame:
    """Append lineups with goals against and clean sheet."""

    lineups['Tegendoelpunt'] = 0
    lineups.loc[lineups['Home_Team'], 'Tegendoelpunt'] = score_away
    lineups.loc[~lineups['Home_Team'], 'Tegendoelpunt'] = score_home

    lineups['CleanSheet'] = 0
    lineups.loc[lineups['Home_Team'], 'CleanSheet'] = (score_away == 0)
    lineups.loc[~lineups['Home_Team'], 'CleanSheet'] = (score_home == 0)
    
    return lineups

def extract_match_events(url: str, dim_players: pd.DataFrame) -> pd.DataFrame:

    html_string = open_website_in_client(config.BASE_URL + url)

    club_urls = extract_url_by_class(html_string, 'a', 'team-title')
    match_state = extract_txt_by_class(html_string, 'span', 'match-state')
    #TODO: Quit process if match state is not FT

    final_score = extract_txt_by_class(html_string, 'h3', 'thick scoretime')[0]
    final_score_home = int(extract_txt_from_string(final_score, '([0-9.*])-'))
    final_score_away = int(extract_txt_from_string(final_score, '-([0-9.*])'))

    lineups = extract_team_lineup(html_string)
    lineups = (
        lineups
        .pipe((determine_winning_team, 'lineups'), score_home=final_score_home, score_away=final_score_away)
        .pipe((append_match_events, 'lineups'), html_string=html_string, dim_players=dim_players)
        .pipe((append_assisters, 'lineups'), html_string=html_string)
        .pipe((determine_goals_against, 'lineups'), score_home=final_score_home, score_away=final_score_away)
    )
    lineups['match_url'] = url
    return lineups


# if __name__ == '__main__':
    # url = config.EXAMPLE_MATCH_URLS.get('red_card')
    # result = extract_match_events(url)
    # print(result)
