from enum import Enum
import pandas as pd
import requests
from lxml import html
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from typing import List, Tuple
import re
import codecs


def read_html_from_url(location_to_scrape:str) -> str:
    REQUEST_HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0"}
    result = requests.get(location_to_scrape, headers=REQUEST_HEADERS)
    with open('test_html.txt', 'w', encoding='utf-8') as f:
        f.write(result.text)
    return result.text


def read_html_from_file(location_to_scrape:str) -> str:
    f = codecs.open(location_to_scrape, 'r', encoding='utf-8')
    return f.read()


def read_html_text(location_to_scrape: str) -> str:
    if location_to_scrape.startswith('http'):
        text = read_html_from_url(location_to_scrape)
    else:            
        text = read_html_from_file(location_to_scrape)
    return text


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


def determine_winning_team(score_home: int, score_away: int) -> Enum:
    if score_home > score_away:
        return 1
    elif score_away > score_home:
        return 2
    elif score_home == score_away:
        return 3
    else:
        pass


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

    return full_lineup
    

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
    
    # Starting state: no asissts
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
    ) -> Tuple[List[str], List[str], List[str], List[str], List[str], List[str], List[int]]:
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

                    return_minute_after_image_search(minutes_red_card, '/RC.png', row, child)
                    
    return cards_yellow, cards_red, goals_general, goals_penalty, goals_own, penalty_missed, minutes_red_card
    

def append_match_events(html_string: str, lineups: pd.DataFrame) -> pd.DataFrame:
    """Append the lineups with information on who took part in match events."""
    
    lineups[['KaartGeel', 'KaartRood', 'Goal', 'GoalEigen', 'PenaltyGoal', 'PenaltyGemist']] = 0
    yc, rc, goals, goals_pen, goals_own, pen_mis, rc_min = extract_match_events_from_lineup_container(html_string)
    
    for player_href in yc: lineups.loc[player_href == lineups['Link'], 'KaartGeel'] += 1 
    for player_href in rc: lineups.loc[player_href == lineups['Link'], 'KaartRood'] += 1 
    for player_href in goals: lineups.loc[player_href == lineups['Link'], 'Goal'] += 1 
    for player_href in goals_pen: lineups.loc[player_href == lineups['Link'], 'GoalEigen'] += 1 
    for player_href in goals_own: lineups.loc[player_href == lineups['Link'], 'PenaltyGoal'] += 1 
    for player_href in pen_mis: lineups.loc[player_href == lineups['Link'], 'PenaltyGemist'] += 1 
        
    return lineups

url = 'https://nl.soccerway.com/matches/2022/05/15/netherlands/eredivisie/sbv-vitesse/afc-ajax/3512762/'
filepath = 'test_html.txt' 
html_string = read_html_text(filepath)

club_urls = extract_url_by_class(html_string, 'a', 'team-title')
match_state = extract_txt_by_class(html_string, 'span', 'match-state')
#TODO: Quit process if match state is not FT

final_score = extract_txt_by_class(html_string, 'h3', 'thick scoretime')[0]
final_score_home = extract_txt_from_string(final_score, '([0-9.*])-')
final_score_away = extract_txt_from_string(final_score, '-([0-9.*])')
final_result = determine_winning_team(final_score_home, final_score_away)

lineups = extract_team_lineup(html_string)
linups = append_match_events(html_string, lineups)
lineups = append_assisters(html_string, lineups)

print(lineups.columns)
print(lineups)


# TODO: Add cards to team lineup
# TODO: Add penalties to team lineup
# TODO: Add win/loss to team lineup


