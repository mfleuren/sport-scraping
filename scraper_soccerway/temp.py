from enum import Enum
import pandas as pd
import requests
from lxml import html
from bs4 import BeautifulSoup
from typing import List
import re

def load_html(from_file: bool = False) -> str:
    if not from_file:
        URL = 'https://nl.soccerway.com/matches/2022/05/15/netherlands/eredivisie/sbv-vitesse/afc-ajax/3512762/'
        REQUEST_HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0"}
        result = requests.get(URL, headers=REQUEST_HEADERS)
        with open('test_html.txt', 'w', encoding='utf-8') as f:
            f.write(result.text)
        return result.text
    else:
        import codecs
        f = codecs.open('test_html.txt', 'r', encoding='utf-8')
        return f.read()
    
tree = html.fromstring(load_html(from_file=True))
soup = BeautifulSoup(load_html(from_file=True), 'html.parser')


def extract_url_by_class(level:str, class_str:str) -> List[str]:
    return tree.xpath(f'//{level}[@class="{class_str}"]/@href')


def extract_txt_by_class(level:str, class_str:str) -> List[str]:
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


def find_all_links_in_table(html: BeautifulSoup) -> List:
    links = []
    for tr in html.findAll("tr"):
        trs = tr.findAll("td")
        for each in trs:
            try:
                link = each.find('a')['href']
                links.append(link)
            except:
                pass
    return links


def extract_team_lineup(html: BeautifulSoup) -> pd.DataFrame:
    lineup = pd.read_html(str(html), encoding='utf-8')[0]
    lineup['Link'] = find_all_links_in_table(html)
    return lineup


club_urls = extract_url_by_class('a', 'team-title')
match_state = extract_txt_by_class('span', 'match-state')
#TODO: Quit process if match state is not FT

final_score = extract_txt_by_class('h3', 'thick scoretime')[0]
final_score_home = extract_txt_from_string(final_score, '([0-9.*])-')
final_score_away = extract_txt_from_string(final_score, '-([0-9.*])')
final_result = determine_winning_team(final_score_home, final_score_away)

lineups_html = soup.find('div', class_='combined-lineups-container')
lineups_home = extract_team_lineup(lineups_html.find('div', class_='container left'))
lineups_away = extract_team_lineup(lineups_html.find('div', class_='container right'))


print(lineups_home, lineups_away)

# TODO: Subs