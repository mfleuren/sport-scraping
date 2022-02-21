import pandas as pd

import sys
sys.path.append('.')
import webscraper

BASE_URL = 'https://www.procyclingstats.com/race/'
YEAR = 2021
BASE_EPITHET = 'result'

selected_matches = pd.read_csv('matches.csv', sep=';')

for url_epi in selected_matches['url_epithet']:

    url = BASE_URL + url_epi + '/' + str(YEAR) + '/' + BASE_EPITHET

    print(url)

    try:
        webscraper.scrape_website(url)
    except:
        print(f"{url} not working")