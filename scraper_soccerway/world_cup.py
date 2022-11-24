from data_processing import CompetitionData
import gather_logic, validate, points_logic

data = CompetitionData()
# data = gather_logic.update_matches(data)
# data = gather_logic.update_players(data)
data = gather_logic.create_full_team_selections(data)
validate.tactics(data.chosen_teams)

data = gather_logic.scrape_matches(data)

data = points_logic.calculate_point_by_player(data)
data = points_logic.calculate_points_by_coach(data)

data.save_files_to_results()

# import generate_figures
# generate_figures.generate_lineups(data.chosen_teams)

