import os
# import sys

# sys.path.append('.')
from scraper_pcs import webscraper, import_files

COMPETITION_NAME = 'Voorjaar'
COMPETITION_YEAR = 2022
COMPETITION_YEAR_NAME = str(COMPETITION_YEAR) + '_' + COMPETITION_NAME

BASE_URL = 'https://www.procyclingstats.com/race/'
YEAR = 2021
BASE_EPITHET = 'result'

# Import CSV Files as Pandas DataFrames
df_teams, df_matches, df_points = import_files(COMPETITION_YEAR_NAME)



# for url_epi in df_matches['url_epithet']:

#     url = BASE_URL + url_epi + '/' + str(YEAR) + '/' + BASE_EPITHET

#     print(url)

#     try:
#         webscraper.scrape_website(url)
#     except:
#         print(f"{url} not working")