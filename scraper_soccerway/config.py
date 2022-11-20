TOURNAMENT_NAME = 'world-cup'
TOURNAMENT_YEAR = 2022
TOURNAMENT_ID_GROUP = 'r49519'
TOURNAMENT_ID_FINALS = 's16394'
TOURNAMENT_CONTINENT = "world"
TOURNAMENT_NATION = "qatar"
TOURNAMENT_START_OF_KO = '2022-12-03'

DEFAULT_SLEEP_S = 1

REGEXES = {
    'team_name_from_url':r'teams/netherlands/(.*)/.*/',
    'team_id_from_url':r'teams/netherlands/.*/(.*)/',
    'player_name_from_url':r'players/(.*)/.*/',
    'player_id_from_url':r'players/.*/(.*)/',
    'match_id_from_url':r'/matches/.*/.*/.*/.*/.*/.*/.*/(.*)/',
    'nation_name_from_url':r'teams/(.*)/.*/.*/',
    'nation_id_from_url':r'teams/.*/.*/(.*)/'
}

BASE_URL = 'https://nl.soccerway.com'
URLS = {
    'matches_group':f"{BASE_URL}/international/{TOURNAMENT_CONTINENT}/{TOURNAMENT_NAME}/{TOURNAMENT_YEAR}-{TOURNAMENT_NATION}/group-stage/{TOURNAMENT_ID_GROUP}/matches/",
    'matches_finals':f"{BASE_URL}/international/{TOURNAMENT_CONTINENT}/{TOURNAMENT_NAME}/{TOURNAMENT_YEAR}-{TOURNAMENT_NATION}/{TOURNAMENT_ID_FINALS}/final-stages/",
    'start_teams':f"{BASE_URL}/international/{TOURNAMENT_CONTINENT}/{TOURNAMENT_NAME}/{TOURNAMENT_YEAR}-{TOURNAMENT_NATION}/group-stage/{TOURNAMENT_ID_GROUP}",
    'teams':"{base_url}/teams/{team_name}/{team_name}/{team_id}/squad/",
}

ALLOWED_TACTICS = ['1343', '1352', '1433', '1442', '1451', '1541', '1532']

EXAMPLE_MATCH_URLS = {
    'squad':'https://nl.soccerway.com/teams/netherlands/sportclub-heerenveen/1519/squad/',
    'matches':'https://nl.soccerway.com/teams/netherlands/sportclub-heerenveen/1519/matches/',
    'clubs':'https://nl.soccerway.com/national/netherlands/eredivisie/20222023/regular-season/r69885/tables/',
    'default':'https://nl.soccerway.com/matches/2022/05/15/netherlands/eredivisie/sbv-vitesse/afc-ajax/3512762/',
    'pen_missed':'https://nl.soccerway.com/matches/2022/08/05/netherlands/eerste-divisie/stichting-heracles-almelo/hfc-ado-den-haag/3798124/',
    'red_card':'https://nl.soccerway.com/matches/2022/08/05/netherlands/eerste-divisie/nac-bv/stichting-helmond-sport/3798125/',
}
EXAMPLE_TXT_PATH = 'scraper_soccerway\html_examples'