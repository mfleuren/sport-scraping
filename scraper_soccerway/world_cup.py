from data_processing import CompetitionData
import gather

# data = CompetitionData()
url = 'https://nl.soccerway.com/international/europe/european-championships/2020/group-stage/r38188/matches/'
result = gather.extract_matches_from_html(url)
print(result.head())
print(result.shape)