from distutils.util import strtobool
import os

from competition_data import CompetitionData
import forum_message
import gather_logic, validate, points_logic
from utility import forum_robot

data = CompetitionData("eredivisie-2022")

data = gather_logic.update_matches(data)
data = gather_logic.update_players(data)

matches_to_scrape = gather_logic.determine_matches_to_scrape(data)
rounds_to_scrape = matches_to_scrape["Cluster"].unique()

print(f"Scraping the following round(s): {', '.join(rounds_to_scrape.astype(str))}")
for game_round in rounds_to_scrape:

    data = gather_logic.create_full_team_selections(data, game_round)
    validate.tactics(data.chosen_teams)

    data = gather_logic.scrape_matches(data, matches_to_scrape, game_round)

    data = points_logic.calculate_point_by_player(data)
    data = points_logic.calculate_points_by_coach(data)

data.save_files_to_results()

final_message = forum_message.create_message(data, rounds_to_scrape)

# print(final_message)
if strtobool(os.getenv("IMGUR_UPLOAD")) and strtobool(os.getenv("FORUM_POST")):
    forum_robot.post_results_to_forum(final_message)
