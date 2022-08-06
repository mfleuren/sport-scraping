from enum import Enum
import pandas as pd
import requests
from lxml import html
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from typing import List, Tuple
import re
import codecs
import os


EXAMPLE_MATCH_URLS = {
    'squad':'https://nl.soccerway.com/teams/netherlands/sportclub-heerenveen/1519/squad/',
    'default':'https://nl.soccerway.com/matches/2022/05/15/netherlands/eredivisie/sbv-vitesse/afc-ajax/3512762/',
    'pen_missed':'https://nl.soccerway.com/matches/2022/08/05/netherlands/eerste-divisie/stichting-heracles-almelo/hfc-ado-den-haag/3798124/',
    'red_card':'https://nl.soccerway.com/matches/2022/08/05/netherlands/eerste-divisie/nac-bv/stichting-helmond-sport/3798125/',
}
EXAMPLE_TXT_PATH = 'scraper_soccerway\html_examples'


def read_html_from_url(location_to_scrape: str, scenario_file: str = None) -> str:
    """Read html from URL and save as txt file if desired."""
    REQUEST_HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0"}
    result = requests.get(location_to_scrape, headers=REQUEST_HEADERS)

    if scenario_file:
        with open(file=scenario_file, mode='x', encoding='utf-8') as f:
            f.write(result.text)
        print(f'Saved scraping result as {scenario_file}')

    return result.text


def load_sample(scenario: str) -> str:
    """Load a sample, either from file or from url."""

    scenario_file = os.path.join(os.getcwd(), EXAMPLE_TXT_PATH, f'{scenario}.txt')
    scenario_file_exists = os.path.exists(scenario_file)
    print(f'{scenario_file} exists: {scenario_file_exists}')

    if scenario_file_exists:
        html_string = read_html_from_file(scenario_file)
    else:
        if example_match in EXAMPLE_MATCH_URLS.keys():
            url = EXAMPLE_MATCH_URLS[example_match]
        else: 
            print(f'Example match name {example_match} not found, scraping default url.')
            url = EXAMPLE_MATCH_URLS['default']
        html_string = read_html_from_url(url, scenario_file)    

    return html_string


def read_html_from_file(location_to_scrape:str) -> str:
    f = codecs.open(location_to_scrape, 'r', encoding='utf-8')
    return f.read()


def read_html_text(location_to_scrape: str) -> str:
    if location_to_scrape.startswith('http'):
        text = read_html_from_url(location_to_scrape)
    else:            
        text = read_html_from_file(location_to_scrape)
    return text


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


def determine_winning_team(score_home: int, score_away: int, lineups: pd.DataFrame) -> pd.DataFrame:
    """Fill Win/Loss/Draw columns in lineups"""

    # Pre-allocate values for columns Winst, Verlies and Gelijkspel
    lineups[['Win', 'Loss', 'Draw']] = False

    if score_home > score_away:
        lineups.loc[lineups['Home_Team'], 'Win'] = True
        lineups.loc[~lineups['Home_Team'], 'Loss'] = True
    elif score_away > score_home:
        lineups.loc[lineups['Home_Team'], 'Loss'] = True
        lineups.loc[~lineups['Home_Team'], 'Win'] = True
    else:
        lineups['Draw'] = True
    
    return lineups


def find_all_links_in_table(soup: BeautifulSoup) -> List: 
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


def parse_html_table(soup: BeautifulSoup) -> pd.DataFrame:
    """Parse html table to dataframe. Remove column Kaarten if it exists."""
    
    df = pd.read_html(str(soup), encoding='utf-8')[0]
    if 'Kaarten' in df.columns:
        df.drop('Kaarten', axis=1, inplace=True)
    
    return df


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
    lineups = parse_html_table(soup_lineup)
    lineups['Link'] = find_all_links_in_table(soup_lineup)

    soup_subs = soup_lineups[1].find('div', class_='container '+position)
    subs = parse_html_table(soup_subs)
    subs['Link'] = find_all_links_in_table(soup_subs)

    full_lineup = find_substitutions(subs, lineups)
    full_lineup.reset_index(drop=True, inplace=True)

    # Drop the coach
    full_lineup = full_lineup[~full_lineup['Speler'].str.contains('Coach:', regex=False)]

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
    
    assisters = determine_assisters(html_string)
    for assister in assisters: lineups.loc[assister == lineups['Link'], 'Assist'] += 1 
        
    return lineups


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
           
    
def extract_match_events_from_lineup_container(
    html_string: str
    ) -> Tuple[List[str], List[str], List[str], List[str], List[str], List[str], List[int], List[int]]:
    """Extract important match events from the HTML, return as a tuple of lists"""

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
    

def append_match_events(html_string: str, lineups: pd.DataFrame) -> pd.DataFrame:
    """Append the lineups with information on who took part in match events."""
    
    lineups[['KaartGeel', 'KaartRood', 'Goal', 'GoalEigen', 'PenaltyGoal', 'PenaltyGemist']] = 0
    yc, rc, goals, goals_pen, goals_own, pen_mis, rc_min, pen_mis_min = extract_match_events_from_lineup_container(html_string)
    
    for player_href in yc: lineups.loc[player_href == lineups['Link'], 'KaartGeel'] += 1      
    for player_href in goals: lineups.loc[player_href == lineups['Link'], 'Goal'] += 1 
    for player_href in goals_pen: lineups.loc[player_href == lineups['Link'], 'GoalEigen'] += 1 
    for player_href in goals_own: lineups.loc[player_href == lineups['Link'], 'PenaltyGoal'] += 1 
    
    # Red Card has extra logic for minutes played
    for player_href, minutes in zip(rc, rc_min): 
        lineups.loc[player_href == lineups['Link'], 'KaartRood'] += 1
        lineups.loc[player_href == lineups['Link'], 'Minuten_Gespeeld'] -= (90-minutes)

    # Penalty missed: extra logic to give active goalkeeper of opposition a +1 on PenaltyStopped
    # TODO: This needs info on player positions (G)
    for player_href, minutes in zip(pen_mis, pen_mis_min):
        lineups.loc[player_href == lineups['Link'], 'PenaltyGemist'] += 1     

    return lineups


def extract_squad_from_html(html_string: str) -> pd.DataFrame:
    """Extracts squad information from HTML."""

    soup = BeautifulSoup(html_string, 'html.parser')
    result = parse_html_table(soup)
    result_short = result[['Unnamed: 0', 'Naam', 'P']].rename({'Unnamed: 0':'Rugnummer', 'P':'Positie'}, axis=1)

    # Append with player links
    soup_squad = soup.find_all('div', class_='squad-container')
    player_urls = remove_duplicates_from_list(find_all_links_in_table(soup_squad[0]))
    result_short['Link'] = player_urls[:-1] # Do not include the last person, the coach
    
    return result_short


def extract_matches_from_html(html_string: str) -> pd.DataFrame:
    """Extract info from matches table."""

    # Extract basic table 
    soup = BeautifulSoup(html_string, 'html.parser')
    result = parse_html_table(soup)
    result.columns = ['Datum', 'Competitie', 'Thuisteam', 'Uitslag', 'Uitteam', 'x1', 'x2']

    # Extract URLS
    soup_matches = soup.find_all('table', class_='matches')
    all_urls = find_all_links_in_table(soup_matches[0])
    all_urls_no_events = [url for url in all_urls if '#events' not in url]    
    chunk_size = 4
    urls_in_chunks = [all_urls_no_events[i:i+chunk_size] for i in range(0, len(all_urls_no_events), chunk_size)]    
    result[['x3', 'url_club_home', 'url_match', 'url_club_away']] = urls_in_chunks

    # Filter only Eredivisie
    result = result[result['Competitie'] == 'ERE']

    # Drop unnecessary columns
    result.drop(['x1', 'x2', 'x3'], axis=1, inplace=True)
    return result


# Select example match
example_match = 'matches'
html_string = load_sample(example_match)

if example_match == 'squad':
    squad = extract_squad_from_html(html_string)
elif example_match == 'clubs':
    pass
elif example_match == 'matches':
    matches =  extract_matches_from_html(html_string)
else:
    club_urls = extract_url_by_class(html_string, 'a', 'team-title')
    match_state = extract_txt_by_class(html_string, 'span', 'match-state')
    #TODO: Quit process if match state is not FT

    final_score = extract_txt_by_class(html_string, 'h3', 'thick scoretime')[0]
    final_score_home = extract_txt_from_string(final_score, '([0-9.*])-')
    final_score_away = extract_txt_from_string(final_score, '-([0-9.*])')

    lineups = extract_team_lineup(html_string)
    lineups = (
        lineups
        .pipe((determine_winning_team, 'lineups'), score_home=final_score_home, score_away=final_score_away)
        .pipe((append_match_events, 'lineups'), html_string=html_string)
        .pipe((append_assisters, 'lineups'), html_string=html_string)
    )

    print(lineups.columns)
    print(lineups)

    # TODO: Add penalty stopped to goalkeeper

    






