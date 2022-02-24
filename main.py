import os

from scraper_pcs.import_files import load_csv_files

COMPETITION_NAME = 'Voorjaar'
COMPETITION_YEAR = 2022
COMPETITION_YEAR_NAME = str(COMPETITION_YEAR) + '_' + COMPETITION_NAME

BASE_URL = 'https://www.procyclingstats.com/race/'
YEAR = 2021
BASE_EPITHET = 'result'

# Import CSV Files as Pandas DataFrames
path_csv_files = os.path.join(os.path.dirname(os.path.realpath(__file__)), COMPETITION_YEAR_NAME) 
df_teams, df_matches, df_points = load_csv_files(path_csv_files)

print(df_matches.head())


# for url_epi in df_matches['url_epithet']:

#     url = BASE_URL + url_epi + '/' + str(YEAR) + '/' + BASE_EPITHET

#     print(url)

#     try:
#         webscraper.scrape_website(url)
#     except:
#         print(f"{url} not working")