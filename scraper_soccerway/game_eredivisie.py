from competition_data import CompetitionData
from forum_message import Message
import gather_logic, validate, points_logic
from utility import forum_robot

data = CompetitionData("eredivisie-2022")
message = Message()

data = gather_logic.update_matches(data)
data = gather_logic.update_players(data)

matches_to_scrape = gather_logic.determine_matches_to_scrape(data)
for game_round in matches_to_scrape["Cluster"].unique():

    data = gather_logic.create_full_team_selections(data, game_round)
    validate.tactics(data.chosen_teams)

    data = gather_logic.scrape_matches(data, matches_to_scrape, game_round)

    data = points_logic.calculate_point_by_player(data)
    data = points_logic.calculate_points_by_coach(data)

    message = message.create_round_ranking(data.points_coach, game_round)

data.save_files_to_results()

message.create_general_ranking(data.points_coach)
message.create_teams_overview(data.points_coach)

final_message = ''.join([message.general_ranking] + [message.teams_overview])

print(final_message)
forum_robot.post_results_to_forum(final_message)

# import generate_figures
# generate_figures.generate_lineups(data.chosen_teams)
