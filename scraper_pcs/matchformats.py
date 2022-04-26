from distutils.util import strtobool
from dotenv import load_dotenv
import os
from datetime import datetime
import time
import pandas as pd
from scraper_pcs.load_save_files import load_csv_files
from scraper_pcs.webscraper import scrape_website
from scraper_pcs.calculate_scores import calculate_match_points, calculate_stage_result
from scraper_pcs.process_results import create_echelon_plot, create_mention_list, create_teams_message, list_best_coaches
from utility import forum_robot, imgur_robot


load_dotenv()
CURRENT_DATE = datetime.now()
PATH_RESULTS = os.path.join(os.getcwd(), 'results', f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}")
MAKE_POST = strtobool(os.getenv('IMGUR_UPLOAD')) and strtobool(os.getenv('FORUM_POST'))
print(f"Value for MAKE_POST: {str(MAKE_POST)} (Upload: {os.getenv('IMGUR_UPLOAD')}, Forum: {os.getenv('FORUM_POST')})")

def spring_classics() -> None:
    # Import CSV Files as Pandas DataFrames
    df_teams, df_matches, df_points, all_results = load_csv_files()

    if all_results.shape[0] > 0:
        matches_to_scrape_indices = (df_matches['MATCH_DATE'] <= CURRENT_DATE) & ~df_matches['MATCH'].isin(all_results['MATCH'].unique())
    else:
        matches_to_scrape_indices = (df_matches['MATCH_DATE'] <= CURRENT_DATE)

    # Select the matches to scrape
    matches_to_scrape = df_matches[matches_to_scrape_indices] 
    img_urls = []
    coach_mentions = []

    for row in matches_to_scrape.iterrows():
        match = row[1]
        print(match['MATCH'])
        plot_name = f"{match['MATCH'].lower()}_plot.png"
        plot_dir = os.path.join(PATH_RESULTS, plot_name)
        print('PLOT DIR ', plot_dir)

        stage_results = scrape_website(match)
        match_points = calculate_match_points(stage_results, df_points, df_teams)
        stage_standing, coach_mentions = calculate_stage_result(match_points, coach_mentions)
        create_echelon_plot(stage_standing, match['MATCH'], plot_dir)

        # TODO: Convert this into a match not posted checker
        if MAKE_POST:# and (match['MATCH'] == matches_to_scrape.iloc[-1]['MATCH']):
            img_url = imgur_robot.upload_to_imgur(plot_name)
            img_urls.append(img_url)

        all_results = all_results.append(match_points)

        time.sleep(1)

    plot_name = 'algemeenklassement_plot.png'
    plot_dir = os.path.join(PATH_RESULTS, plot_name)
    create_echelon_plot(all_results, 'Algemeen Klassement', plot_dir)
    coach_mentions.append(list_best_coaches(all_results))

    if MAKE_POST:
        img_url = imgur_robot.upload_to_imgur(plot_name)
        img_urls.append(img_url)
        image_message = ''.join(img_urls)
        teams_message = create_teams_message(all_results)
        mentions_message = create_mention_list(coach_mentions)
        single_message = image_message + str(mentions_message) + teams_message
        forum_robot.post_results_to_forum(single_message)

        all_results.to_csv('all_results.csv', index=False)

def grand_tour():
    print('Not implemented yet.')