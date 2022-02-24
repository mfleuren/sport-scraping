import pandas as pd

import os
import sys
sys.path.append('.')
import webscraper
import import_files

BASE_URL = 'https://www.procyclingstats.com/race/'
YEAR = 2021
BASE_EPITHET = 'result'

PATH_CURRENT_FILE = os.path.dirname(os.path.realpath(__file__)) 
PATH_CSV_TEAMS = os.path.join(PATH_CURRENT_FILE, 'teams.csv')
PATH_CSV_MATCHES = os.path.join(PATH_CURRENT_FILE, 'matches.csv')
PATH_CSV_POINTS = os.path.join(PATH_CURRENT_FILE, 'points.csv')

# Load CSV-files with teams, match and points information
df_teams = import_files.import_teams(PATH_CSV_TEAMS)
df_matches = import_files.import_matches(PATH_CSV_MATCHES)
df_points = import_files.import_points(PATH_CSV_POINTS)

for url_epi in df_matches['url_epithet']:

    url = BASE_URL + url_epi + '/' + str(YEAR) + '/' + BASE_EPITHET

    print(url)

    try:
        webscraper.scrape_website(url)
    except:
        print(f"{url} not working")