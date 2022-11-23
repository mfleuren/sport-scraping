from data_processing import CompetitionData
import gather_logic, validate

data = CompetitionData()
# data = gather_logic.update_matches(data)
data = gather_logic.update_players(data)
data = gather_logic.create_full_team_selections(data)
validate.tactics(data.chosen_teams)

# data = gather_logic.scrape_matches(data)

data.save_files_to_results()

import generate_figures
generate_figures.generate_lineups(data.chosen_teams)