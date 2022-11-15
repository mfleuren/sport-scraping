from datetime import datetime
import pandas as pd

from data_processing import CompetitionData
import gather_logic, validate


data = CompetitionData()
# data = gather_logic.update_matches(data)
# data = gather_logic.update_players(data)
data = gather_logic.create_full_team_selections(data)
validate.tactics(data.chosen_teams)

matches_to_scrape = gather_logic.determine_matches_to_scrape(data)
print(matches_to_scrape)

# data.save_files_to_results()
