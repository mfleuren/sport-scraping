from distutils.util import strtobool
import os
from datetime import datetime
import time
import pandas as pd
from scraper_pcs.import_files import load_csv_files
from scraper_pcs.webscraper import scrape_website
from scraper_pcs.calculate_scores import calculate_match_points, calculate_stage_result
from scraper_pcs.plot_results import create_echelon_plot
from utility import forum_robot, imgur_robot

from dotenv import load_dotenv

load_dotenv()

CURRENT_DATE = datetime.now()
MAKE_POST = strtobool(os.getenv('IMGUR_UPLOAD')) and strtobool(os.getenv('FORUM_POST'))
print(f"Value for MAKE_POST: {str(MAKE_POST)} (Upload: {os.getenv('IMGUR_UPLOAD')}, Forum: {os.getenv('FORUM_POST')})")

# Import CSV Files as Pandas DataFrames
path_files = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}"
) 
df_teams, df_matches, df_points = load_csv_files(path_files)

# Load previous results or pre-allocate all_results
if os.path.exists(os.path.join(path_files, 'all_results.csv')):
    all_results = pd.read_csv(os.path.join(path_files, 'all_results.csv'))
    matches_to_scrape_indices = (df_matches['MATCH_DATE'] <= CURRENT_DATE) & ~df_matches['MATCH'].isin(all_results['MATCH'].unique())
    print(f'Loaded all_results file, dataframe shape: {all_results.shape}')
else:
    all_results = pd.DataFrame()
    matches_to_scrape_indices = (df_matches['MATCH_DATE'] <= CURRENT_DATE)
    print('Pre-allocate empty dataframe for all_results')

# Select the matches to scrape
matches_to_scrape = df_matches[matches_to_scrape_indices] 
img_urls = []

for row in matches_to_scrape.iterrows():
    match = row[1]
    print(match['MATCH'])
    plot_name = f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}\\{match['MATCH'].lower()}_plot.png"

    stage_results = scrape_website(match)
    match_points = calculate_match_points(stage_results, df_points, df_teams)
    stage_standing = calculate_stage_result(match_points)
    create_echelon_plot(stage_standing, match['MATCH'], plot_name)

    if MAKE_POST and (match['MATCH'] == matches_to_scrape.iloc[-1]['MATCH']):
        img_url = imgur_robot.upload_to_imgur(plot_name)
        img_urls.append(img_url)

    all_results = all_results.append(match_points)


    time.sleep(1)

all_results.to_csv('2022_Voorjaar/all_results.csv', index=False)

plot_name = f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}\\algemeenklassement_plot.png"
create_echelon_plot(all_results, 'Algemeen Klassement', plot_name)

if MAKE_POST:
    img_url = imgur_robot.upload_to_imgur(plot_name)
    img_urls.append(img_url)
    single_message =  ''.join(img_urls)
    print(single_message)
    forum_robot.post_results_to_forum(single_message)