import os
from datetime import datetime
import time
import pandas as pd
from scraper_pcs.import_files import load_csv_files
from scraper_pcs.webscraper import scrape_website
from scraper_pcs.calculate_scores import calculate_match_points, calculate_stage_result
from scraper_pcs.plot_results import create_echelon_plot

from dotenv import load_dotenv

load_dotenv()

CURRENT_DATE = datetime.now()

# Import CSV Files as Pandas DataFrames
path_csv_files = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.getenv('COMPETITION_YEAR_NAME')) 
df_teams, df_matches, df_points = load_csv_files(path_csv_files)

# Pre-allocate all_results
all_results = pd.DataFrame()

# Select the matches to scrape
matches_to_scrape = df_matches[df_matches['MATCH_DATE'] <= CURRENT_DATE]

for row in matches_to_scrape.iterrows():
    match = row[1]
    print(match['MATCH'])
    plot_name = os.getenv('COMPETITINO_YEAR_NAME') + '\\' + match['MATCH'].lower() + '_plot.png'

    stage_results = scrape_website(match)
    match_points = calculate_match_points(stage_results, df_points, df_teams)
    stage_standing = calculate_stage_result(match_points)
    create_echelon_plot(stage_standing, match['MATCH'], plot_name)

    all_results = all_results.append(match_points)


    time.sleep(1)

# print('Algemeen klassement')
# print(all_results.groupby('COACH')['POINTS'].sum().sort_values(ascending=False).astype('int'))
# print(all_results[(all_results['COACH'] == 'Rellende Rotscholier') & (all_results['MATCH'] == 'Drome Classic')])
# all_results.to_csv('2022_Voorjaar/gc.csv', index=False)

plot_name = str(COMPETITION_YEAR) + '_' + COMPETITION_NAME + '\\' + 'algemeenklassement' + '_plot.png'
create_echelon_plot(all_results, 'Algemeen Klassement', plot_name)
