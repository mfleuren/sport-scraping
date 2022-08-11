EXAMPLE_MATCH_URLS = {
    'squad':'https://nl.soccerway.com/teams/netherlands/sportclub-heerenveen/1519/squad/',
    'matches':'https://nl.soccerway.com/teams/netherlands/sportclub-heerenveen/1519/matches/',
    'clubs':'https://nl.soccerway.com/national/netherlands/eredivisie/20222023/regular-season/r69885/tables/',
    'default':'https://nl.soccerway.com/matches/2022/05/15/netherlands/eredivisie/sbv-vitesse/afc-ajax/3512762/',
    'pen_missed':'https://nl.soccerway.com/matches/2022/08/05/netherlands/eerste-divisie/stichting-heracles-almelo/hfc-ado-den-haag/3798124/',
    'red_card':'https://nl.soccerway.com/matches/2022/08/05/netherlands/eerste-divisie/nac-bv/stichting-helmond-sport/3798125/',
}
EXAMPLE_TXT_PATH = 'scraper_soccerway\html_examples'

REGEXES = {
    'team_name_from_url':r'teams/netherlands/(.*)/.*/',
    'team_id_from_url':r'teams/netherlands/.*/(.*)/',
    'player_name_from_url':r'players/(.*)/.*/',
    'player_id_from_url':r'players/.*/(.*)/',
    'match_id_from_url':r'/matches/.*/.*/.*/.*/.*/.*/.*/(.*)/',
}

URLS = {
    'matches':'https://nl.soccerway.com/teams/netherlands/{club_name}/{club_id}/matches/'
}