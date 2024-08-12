import datetime as dt
from dotenv import load_dotenv

load_dotenv("G:\\Local\\sport-scraping\\nations_cup.env")

from competition_data import CompetitionData
from forum_message import Message
import gather_logic, validate, points_logic
from utility import forum_robot

data = CompetitionData("european-championships-2024")

print(data)

data = gather_logic.update_matches(data)
# data = gather_logic.update_players(data)
data = gather_logic.create_full_team_selections(data)
print(f"{data.chosen_teams=}")
print(f"{data.chosen_teams[data.chosen_teams['Team'].isna()]}")
validate.tactics(data.chosen_teams)

if "Match_Url" in data.match_events.columns:
    matches_to_scrape = data.matches[
        (data.matches["Datum"] < dt.datetime.today()) &\
         ~(data.matches["url_match"].isin(data.match_events["Match_Url"].unique()))
         ]
else:
    matches_to_scrape = data.matches[
        (data.matches["Datum"] < dt.datetime.today())
        ]

data = gather_logic.scrape_matches(data, matches_to_scrape)

print(f"{data.match_events=}")

data = points_logic.calculate_point_by_player(data)
data = points_logic.calculate_points_by_coach(data)

data.save_files_to_results()

# import generate_figures
# generate_figures.generate_lineups(data.chosen_teams)

# message = Message()

# message.create_general_ranking(data.points_coach)
# message.create_teams_overview(data.points_coach)

# final_message = ''.join([message.general_ranking] + [message.teams_overview])
# forum_robot.post_results_to_forum(final_message)