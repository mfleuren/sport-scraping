from distutils.util import strtobool
from dotenv import load_dotenv
import os
from datetime import datetime
import time
from scraper_pcs.process_files import load_csv_files
from scraper_pcs.webscraper import scrape_website
from scraper_pcs.calculate_scores import calculate_match_points, calculate_match_standings
from scraper_pcs.process_results import create_echelon_plot, create_mention_list, create_teams_message, list_best_coaches
from utility import forum_robot, imgur_robot
from utility.dataclasses import StageResults, Message


load_dotenv()
CURRENT_DATE = datetime.now()
PATH_RESULTS = os.path.join(os.getcwd(), 'results', f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}")
MAKE_POST = strtobool(os.getenv('IMGUR_UPLOAD')) and strtobool(os.getenv('FORUM_POST'))
print(f"Value for MAKE_POST: {str(MAKE_POST)} (Upload: {os.getenv('IMGUR_UPLOAD')}, Forum: {os.getenv('FORUM_POST')})")


def spring_classics() -> None:

    results_data = StageResults()
    message_data = Message()

    # Import CSV Files as Pandas DataFrames
    df_teams, df_matches, df_points, all_results = load_csv_files()

    # Select the matches to scrape
    match_date_is_in_past = (df_matches['MATCH_DATE'] <= CURRENT_DATE)
    match_not_processed_yet = ~df_matches['MATCH'].isin(all_results['MATCH'].unique())
    matches_to_scrape = df_matches[match_date_is_in_past & match_not_processed_yet] 

    for idx, match in matches_to_scrape.iterrows():
        print(f"Processing match {idx+1} of {matches_to_scrape.shape[0]+1}: {match['MATCH']}.")
    
        results_data = scrape_website(results_data, match)
        results_data = calculate_match_points(results_data, df_points, df_teams)
        results_data, message_data = calculate_match_standings(results_data, message_data)
        create_echelon_plot(results_data)

        # TODO: Convert this into a match not posted checker
        if MAKE_POST:# and (match['MATCH'] == matches_to_scrape.iloc[-1]['MATCH']):
            img_url = imgur_robot.upload_to_imgur(plot_name)
            message_data.img_urls.append(img_url)

        all_results = all_results.append(results_data.stage_points)

        print(message_data)

        time.sleep(1)

    print(message_data)

    plot_name = 'algemeenklassement_plot.png'
    plot_dir = os.path.join(PATH_RESULTS, plot_name)
    create_echelon_plot(all_results, 'Algemeen Klassement', plot_dir)
    message_data.coach_mentions.append(list_best_coaches(all_results))

    if MAKE_POST:
        img_url = imgur_robot.upload_to_imgur(plot_name)
        message_data.img_urls.append(img_url)
        image_message = ''.join(message_data.img_urls)
        teams_message = create_teams_message(all_results)
        mentions_message = create_mention_list(message_data.coach_mentions)
        single_message = image_message + str(mentions_message) + teams_message
        forum_robot.post_results_to_forum(single_message)

        all_results.to_csv('all_results.csv', index=False)

def grand_tour():
    print('Not implemented yet.')