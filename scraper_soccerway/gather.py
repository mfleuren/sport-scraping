import requests
from requests.sessions import Session
import pandas as pd
from bs4 import BeautifulSoup
import datetime

import os
from typing import List

from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.append(os.getcwd())
import config as cfg


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


def extract_clubs_from_html(url: str) -> pd.DataFrame:
    """Extract info from clubs table."""

    # Open website and get HTML
    client = start_webclient()
    get_result = client.get(url)
    print(f'Status code: {get_result.status_code}')
    html_string = get_result.content.decode(get_result.encoding)

    # Extract basic table
    result = pd.read_html(html_string)[0]
    result = result.iloc[:-2]['Team'].to_frame()  

    # Extract URLS
    soup = BeautifulSoup(html_string, 'html.parser')
    soup_clubs = soup.find_all('table', class_='leaguetable sortable table detailed-table')
    all_urls = find_all_links_in_table(soup_clubs[0])
    all_team_urls = [url for url in all_urls if 'teams' in url]
    result['SW_TeamURL'] = all_team_urls
    result['SW_Teamnaam'] = result['SW_TeamURL'].str.extract(cfg.REGEXES['team_name_from_url'], expand=True)
    result['SW_TeamID'] = result['SW_TeamURL'].str.extract(cfg.REGEXES['team_id_from_url'], expand=True).astype('int')
    
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


def extract_matches_from_html(html_string: str) -> pd.DataFrame:
    """Extract info from matches table."""

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

if __name__ == '__main__':

    url = 'https://nl.soccerway.com/national/netherlands/eredivisie/20222023/regular-season/r69885/tables/'
    html_str = open_website_in_client(url)

    clubs = extract_clubs_from_html(html_str)
    print(clubs)
