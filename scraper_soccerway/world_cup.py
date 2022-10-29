from data_processing import CompetitionData
import gather_logic


data = CompetitionData()
# data = gather_logic.update_matches(data)
data = gather_logic.update_players(data)

print(data.dim_players.head())
