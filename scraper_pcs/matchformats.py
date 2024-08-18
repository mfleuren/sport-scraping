from distutils.util import strtobool
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime

load_dotenv("G:\\Local\\sport-scraping\\pcs.env")

import sys
sys.path.append(os.getcwd())
from scraper_pcs.process_substitutions import process_substitutions, create_teams_plot
from scraper_pcs.webscraper import scrape_website
from scraper_pcs.calculate_scores import calculate_match_points, calculate_match_standings, calculate_stage_points
from scraper_pcs import process_results
from utility import forum_robot, result_objects

PATH_RESULTS = os.path.join(os.getcwd(), 'results', f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}")
MAKE_POST = strtobool(os.getenv('IMGUR_UPLOAD')) and strtobool(os.getenv('FORUM_POST'))
print(f"Value for MAKE_POST: {str(MAKE_POST)} (Upload: {os.getenv('IMGUR_UPLOAD')}, Forum: {os.getenv('FORUM_POST')})")


def find_matches_to_scrape(results_data: result_objects.StageResults) -> pd.DataFrame:

    match_date_is_in_past = (results_data.matches['MATCH_DATE'] <= datetime.now())
    match_not_processed_yet = ~results_data.matches['MATCH'].isin(results_data.all_results['MATCH'].unique())
    matches_to_scrape = results_data.matches[match_date_is_in_past & match_not_processed_yet].reset_index(drop=True)

    return matches_to_scrape

def spring_classics() -> None:

    results_data = result_objects.StageResults()
    message_data = result_objects.Message()

    matches_to_scrape = find_matches_to_scrape(results_data)

    for idx, match in matches_to_scrape.iterrows():
        print(f"Processing match {idx+1} of {matches_to_scrape.shape[0]}: {match['MATCH']}.")
    
        results_data = scrape_website(results_data, match)
        results_data = calculate_match_points(results_data)
        results_data, message_data = calculate_match_standings(results_data, message_data)
        message_data = process_results.create_echelon_plot(results_data, message_data, gc=False)

    if len(matches_to_scrape) > 0:
        print("Processing general classification.")
        results_data.append_stages_to_existing_data()
        results_data.export_concatenated_data()

    message_data.coach_mentions.append(process_results.list_best_coaches(results_data.all_points))
    message_data = process_results.create_echelon_plot(results_data, message_data, gc=True)

    single_message = process_results.create_forum_message(results_data, message_data)
    if MAKE_POST:
        forum_robot.post_results_to_forum(single_message)


def grand_tour():

    results_data = result_objects.StageResults()
    message_data = result_objects.Message()

    matches_to_scrape = find_matches_to_scrape(results_data)

    print(matches_to_scrape)

    for idx, match in matches_to_scrape.iterrows():
        print(f"Processing stage {idx+1} of {matches_to_scrape.shape[0]}.")
    
        results_data = scrape_website(results_data, match, stage_race=True)
        results_data = calculate_match_points(results_data, stage_race=True)
        results_data, message_data = process_substitutions(results_data, message_data)
        results_data, message_data = calculate_stage_points(results_data, message_data)
        message_data = process_results.create_swarm_plot(results_data, message_data, gc_check=False)
    
    if len(matches_to_scrape) > 0:
        print("Processing general classification.")
        results_data.append_stages_to_existing_data()

    message_data.coach_mentions.append(process_results.list_best_coaches(results_data.all_points[results_data.all_points['POSITION'] == 'In']))
    message_data = process_results.create_swarm_plot(results_data, message_data, gc_check=True)
    message_data = create_teams_plot(results_data, message_data)
    print(message_data)

    single_message = process_results.create_forum_message(results_data, message_data)
    print(single_message)
    with open("output.txt", "w") as f:
        f.write(single_message)
    # if MAKE_POST:
    #     forum_robot.post_results_to_forum(single_message)

    results_data.export_concatenated_data()
    results_data.export_teams()


if __name__ == '__main__':
    grand_tour()

