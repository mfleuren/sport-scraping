from enum import Enum
import pandas as pd
import requests
from lxml import html
from bs4 import BeautifulSoup
from bs4.element import ResultSet
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
    return pd.read_html(str(soup), encoding='utf-8')[0]


def find_replacements(subs_df: pd.DataFrame, base_df: pd.DataFrame) -> pd.DataFrame:

    subs_df_split = (subs_df['Speler'].str.split('([\w\s\.]+) for ([\w\s\.]+) ([0-9]+)\'', expand=True))
    all_subs = subs_df_split[1].fillna(subs_df_split[0]).rename('Speler')
    sub_minutes_played = 90-subs_df_split[3].fillna(90).astype('int').rename('Minuten_Gespeeld')
    subs_df2 = pd.concat([subs_df['#'], all_subs, subs_df[['Kaarten', 'Link']], sub_minutes_played], axis=1)

    players_out = subs_df_split[2].rename('Speler')
    players_out_minutes_played = subs_df_split[3].fillna(90).astype('int').rename('Minuten_Gespeeld')
    players_out_df = pd.concat([players_out, players_out_minutes_played], axis=1).dropna()

    print(players_out_df)

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

    full_lineup = find_replacements(subs, lineups)

    return full_lineup
    

def extract_team_lineup(html_string: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Extract the full team lineups and minutes played for home and away teams."""
    soup = BeautifulSoup(html_string, 'html.parser')
    soup_lineups = soup.find_all('div', class_='combined-lineups-container')

    full_lineup_home = extract_lineup_from_html(soup_lineups, 'left')
    full_lineup_away = extract_lineup_from_html(soup_lineups, 'right')

    return full_lineup_home, full_lineup_away
    

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

lineup_home, lineup_away = extract_team_lineup(html_string)


