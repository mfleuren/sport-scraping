import os
from datetime import datetime
from scraper_pcs.import_files import load_csv_files
from scraper_pcs.webscraper import scrape_website

COMPETITION_NAME = 'Voorjaar'
COMPETITION_YEAR = 2022
COMPETITION_YEAR_NAME = str(COMPETITION_YEAR) + '_' + COMPETITION_NAME

BASE_URL = 'https://www.procyclingstats.com/race/'
YEAR = datetime.now().year
BASE_EPITHET = 'result'

CURRENT_DATE = datetime.now()

# Import CSV Files as Pandas DataFrames
path_csv_files = os.path.join(os.path.dirname(os.path.realpath(__file__)), COMPETITION_YEAR_NAME) 
df_teams, df_matches, df_points = load_csv_files(path_csv_files)

# Select the matches to scrape
matches_to_scrape = df_matches[df_matches['MATCH_DATE'] <= CURRENT_DATE]

for url_epi in [matches_to_scrape.iloc[0]['URL_EPITHET']]:

    url = BASE_URL + url_epi + '/' + str(YEAR) + '/' + BASE_EPITHET

    print(url)

    try:
        stage_results = scrape_website(url)
        stage_results.to_csv('temp/results_example.csv')        

    except:
        print(f"{url} not working")