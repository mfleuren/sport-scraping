import time
from tqdm import tqdm
import pandas as pd
from unidecode import unidecode

from scraper_soccerway import gather, config
from scraper_soccerway.data_processing import CompetitionData


def construct_url(fmt_url: str, team: str, id: str) -> str:
    return fmt_url.format(base_url=config.BASE_URL, team_name=team, team_id=id)  


def update_matches(data: CompetitionData) -> CompetitionData:
    """Loop through all club URLs and update match dates and match URLs."""

    urls = [config.URLS['matches_group'], config.URLS['matches_finals']]

    for url in tqdm(urls, total=len(urls)):

        updated_matches = gather.extract_matches_from_html_tournament(url, chunk_size=3)
        data.matches = pd.concat([data.matches, updated_matches], ignore_index=True)

        time.sleep(config.DEFAULT_SLEEP_S)

    # If a match_id is duplicated, only keep the last entry (most up to date)
    duplicated_mask = data.matches.duplicated(subset=['url_match'], keep='last')
    data.matches = data.matches[~duplicated_mask]

    return data


def update_players(data: CompetitionData) -> CompetitionData:

    def check_duplicates(df: pd.DataFrame, diff_col: str = None, keep: str = 'last') -> pd.Series:
        
        cols_to_drop_constant = ['Rugnummer', 'Naam', 'Naam_fix', 'Positie_Order', 'Team_Order', 'Naam_Order']
        cols_to_drop = [diff_col] + cols_to_drop_constant if diff_col else cols_to_drop_constant
        columns_to_check = df.columns[~df.columns.isin(cols_to_drop)]
        duplicated_mask = df.duplicated(subset=columns_to_check, keep=keep)

        if not diff_col: return duplicated_mask

        if (duplicated_mask.sum() > 0) & (keep == 'last'):
            print(f'Found {duplicated_mask.sum()} changes in column {diff_col}')

            all_duplicates_mask = df.duplicated(subset=columns_to_check, keep=False)
            changes = df[all_duplicates_mask].groupby('Naam').agg({diff_col:['first', 'last']})

            for name,row in changes.iterrows():
                print(f"\t{name:16s}\t{row[diff_col]['first']:>12s}  -->  {row[diff_col]['last']:12s}")              
        return duplicated_mask

    all_players = data.dim_players.copy()
    for _,row in tqdm(data.dim_clubs.iterrows(), total=data.dim_clubs.shape[0]):

        match_url = construct_url(config.URLS['teams'], row['SW_Teamnaam'], row['SW_TeamID'])
        players_for_club = gather.extract_squad_from_html(match_url, remove_coach=False)
        players_for_club['Team'] = row['Team']
        all_players = pd.concat([all_players, players_for_club], ignore_index=True)
        time.sleep(config.DEFAULT_SLEEP_S)       

    # Remove completely duplicated rows
    duplicated_mask = check_duplicates(df=all_players)
    all_players = all_players[~duplicated_mask].copy()

    # Check for players that changed position - keep the original row
    duplicated_mask_pos = check_duplicates(df=all_players, diff_col='Positie', keep='first')
    all_players = all_players[~duplicated_mask_pos].copy()

    # Check for players that changed club - keep the new row
    duplicated_mask_team = check_duplicates(df=all_players, diff_col='Team', keep='last')
    all_players = all_players[~duplicated_mask_team].copy() 

    all_players['Naam_fix'] = all_players.apply(lambda x: unidecode(x['Naam']), axis=1)
    data.dim_players = all_players.sort_values(by='SW_ID')

    return data


def create_full_team_selections(data: CompetitionData) -> CompetitionData:

    data.chosen_teams = pd.merge(data.chosen_teams, data.dim_players, left_on='Speler', right_on='Naam_fix', how='left')

    return data

