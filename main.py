import os
from datetime import datetime
import time
from scraper_pcs.import_files import load_csv_files
from scraper_pcs.webscraper import scrape_website


COMPETITION_NAME = 'Voorjaar'
COMPETITION_YEAR = 2022
COMPETITION_YEAR_NAME = str(COMPETITION_YEAR) + '_' + COMPETITION_NAME

CURRENT_DATE = datetime.now()

# Import CSV Files as Pandas DataFrames
path_csv_files = os.path.join(os.path.dirname(os.path.realpath(__file__)), COMPETITION_YEAR_NAME) 
df_teams, df_matches, df_points = load_csv_files(path_csv_files)

# Select the matches to scrape
matches_to_scrape = df_matches[df_matches['MATCH_DATE'] <= CURRENT_DATE]

for row in matches_to_scrape.iterrows():
    match = row[1]

    print(match['MATCH'])
    try:
        stage_results = scrape_website(match)
        stage_results.to_csv('temp/results_example.csv', index=False)        

    except:
        print(f"{match['MATCH']} not working")

    time.sleep(1)