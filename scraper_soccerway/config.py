COMPETITION_SETTINGS = {
    "eredivisie-2022": {
        "NAME":"Eredivisie",
        "YEAR":"2022",
        "TOURNAMENT":False,
        "ID":"r69885", 
        "URLS": {
            "matches":"{base_url}/teams/netherlands/{team_name}/{team_id}/matches/",
            "teams":"{base_url}/teams/netherlands/{team_name}/{team_id}/squad/",
            "teams_start":"{base_url}/national/netherlands/eredivisie/{year}/regular-season/{id}/tables/"
        }
    },
    "world-cup-2022": {
        "NAME":"world-cup",
        "YEAR":2022,
        "TOURNAMENT":True,
        "ID_GROUP":"r49519",
        "ID_FINALS":"s16394",
        "CONTINENT":"world",
        "NATION":"qatar",
        "START_OF_KO":"2022-12-03",
        "URLS": {
            "matches_group":"{base_url}/international/{continent}/{name}/{year}-{nation}/group-stage/{id_group}/matches/",
            "matches_finals":"{base_url}/international/{continent}/{name}/{year}-{nation}/{id_finals}/final-stages/",
            "start_teams":"{base_url}/international/{continent}/{name}/{year}-{nation}/group-stage/{id_group}",
            "teams":"{base_url}/teams/{team_name}/{team_name}/{team_id}"
        }
    }
}

LOCAL_FILES = {
    "teams":"teams.csv",
    "substitutions":"substitutions.csv",
    "substitutions_free":"free_substitutions.csv",
    "points_scheme":"points_scheme.csv",
    "points_player":"points_player.csv",
    "points_coach":"points_coach.csv",
    "clubs":"dim_clubs.csv",
    "players":"dim_players.csv",
    "matches":"matches.csv",
    "match_events":"match_events.csv"
}

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