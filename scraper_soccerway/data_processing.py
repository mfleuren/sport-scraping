from typing import Union
from dataclasses import dataclass, field
from wsgiref import validate
from unidecode import unidecode

import os
import time
from datetime import date
from tqdm import tqdm
import pandas as pd


import config, gather 

from dotenv import load_dotenv
load_dotenv()


# Football input
FOOTBALL_PATH_INPUT = os.path.join(
    os.getcwd(), 
    'inputs', 
    f"{os.getenv('FOOTBALL_COMPETITION_YEAR')}_{os.getenv('FOOTBALL_COMPETITION_NAME')}"
    )
FOOTBALL_PATH_RESULTS = os.path.join(
    os.getcwd(), 
    'results', 
    f"{os.getenv('FOOTBALL_COMPETITION_YEAR')}_{os.getenv('FOOTBALL_COMPETITION_NAME')}"
    )

FILE_FOOTBALL_TEAMS_INPUT = os.path.join(FOOTBALL_PATH_INPUT, 'teams.csv')
FILE_FOOTBALL_SUBSTITUTIONS = os.path.join(FOOTBALL_PATH_INPUT, 'substitutions.csv')
FILE_FOOTBALL_POINTS_SCHEME = os.path.join(FOOTBALL_PATH_INPUT, 'points_scheme.csv')

FILE_FOOTBALL_TEAMS_RESULTS = os.path.join(FOOTBALL_PATH_RESULTS, 'teams.csv')
FILE_FOOTBALL_POINTS_PLAYER = os.path.join(FOOTBALL_PATH_RESULTS, 'points_player.csv')
FILE_FOOTBALL_POINTS_COACH = os.path.join(FOOTBALL_PATH_RESULTS, 'points_coach.csv')
FILE_FOOTBALL_DIM_CLUBS = os.path.join(FOOTBALL_PATH_RESULTS, 'dim_clubs.csv')
FILE_FOOTBALL_DIM_PLAYERS = os.path.join(FOOTBALL_PATH_RESULTS, 'dim_players.csv')
FILE_FOOTBALL_MATCHES = os.path.join(FOOTBALL_PATH_RESULTS, 'matches.csv')
FILE_FOOTBALL_MATCH_EVENTS = os.path.join(FOOTBALL_PATH_RESULTS, 'match_events.csv')

FOOTBALL_YEAR = os.getenv('FOOTBALL_COMPETITION_YEAR')
FOOTBALL_YEARCODE = FOOTBALL_YEAR + str(int(FOOTBALL_YEAR)+1)
FOOTBALL_COMPETITION_CODE = os.getenv('FOOTBALL_COMPETITION_CODE')

"""
GENERAL USE FUNCTIONS
"""

def construct_url(fmt_url: str, club: str, id: str) -> str:
    return fmt_url.format(club_name=club, club_id=id)  

"""
DATACLASSES FOR FOOTBALL SCRAPERS
"""

@dataclass
class CompetitionData:
    chosen_teams: pd.DataFrame = field(init=False)
    substitutions: pd.DataFrame = field(init=False)
    points_scheme: pd.DataFrame = field(init=False)
    points_player: pd.DataFrame = field(init=False)
    points_coach: pd.DataFrame = field(init=False)
    dim_clubs: pd.DataFrame = field(init=False)
    dim_players: pd.DataFrame = field(init=False)
    matches: pd.DataFrame = field(init=False)
    match_events: pd.DataFrame = field(init=False)


    def __post_init__(self):
        self.chosen_teams = self.load_file_from_input_or_results(FILE_FOOTBALL_TEAMS_INPUT, FILE_FOOTBALL_TEAMS_RESULTS)
        self.substitutions = pd.read_csv(FILE_FOOTBALL_SUBSTITUTIONS, sep=';')
        self.points_scheme = pd.read_csv(FILE_FOOTBALL_POINTS_SCHEME, sep=';')
        self.points_player = self.load_file_from_results(FILE_FOOTBALL_POINTS_PLAYER)
        self.points_coach = self.load_file_from_results(FILE_FOOTBALL_POINTS_COACH)
        self.dim_clubs = self.load_clubs(FILE_FOOTBALL_DIM_CLUBS)
        self.dim_players = self.load_file_from_results(FILE_FOOTBALL_DIM_PLAYERS)
        self.matches = self.load_file_from_results(FILE_FOOTBALL_MATCHES)
        self.match_events = self.load_file_from_results(FILE_FOOTBALL_MATCH_EVENTS)


    def load_file_from_input_or_results(self, 
        input_path: Union[str, os.PathLike], 
        result_path: Union[str, os.PathLike]
        ) -> pd.DataFrame:
        """
        Logic to determine which teams file to initialize:
        - If results file exists: use results
        - Else if input file exists: use inputs
        - Else: Error
        """

        try:
            if os.path.exists(result_path):
                df = pd.read_csv(result_path, sep=';')

                if 'Datum' in df.columns:
                    df['Datum'] = pd.to_datetime(df['Datum'], format='%d-%m-%Y')

                print(f'Loaded file {result_path} from result.')
                return df

            elif os.path.exists(input_path):
                df = pd.read_csv(input_path, sep=';')

                print(f'Loaded file {input_path} from input.')
                return df

            else:
                raise Exception(input_path, result_path)

        except Exception:
            print(f'Unexpected Exception. Files {input_path} and {result_path} both not found.')
            raise


    def load_file_from_results(self, path: Union[str, os.PathLike]) -> pd.DataFrame:
        """Load file from Results folder, if not exists pre-allocate empty DataFrame."""
        return pd.read_csv(path, sep=';') if os.path.exists(path) else pd.DataFrame()


    def save_files_to_results(self) -> None:
        """Save datafile to Results folder"""

        if self.matches.shape[0] != 0:
            self.matches.to_csv(FILE_FOOTBALL_MATCHES, sep=';', index=False)
            print('Saved matches data to disk.')

        if self.dim_players.shape[0] != 0:
            self.dim_players.to_csv(FILE_FOOTBALL_DIM_PLAYERS, sep=';', index=False)
            print('Saved players data to disk.')

        if self.chosen_teams.shape[0] != 0:
            self.chosen_teams.to_csv(FILE_FOOTBALL_TEAMS_RESULTS, sep=';', index=False)
            print('Saved chosen teams data to disk.')

        if self.points_player.shape[0] != 0:
            self.points_player.to_csv(FILE_FOOTBALL_POINTS_PLAYER, sep=';', index=False)
            print('Saved points by player data to disk.')

        if self.points_coach.shape[0] != 0:
            self.points_coach.to_csv(FILE_FOOTBALL_POINTS_COACH, sep=';', index=False)
            print('Saved points by coach data to disk.')

        if self.match_events.shape[0] != 0:
            self.match_events.to_csv(FILE_FOOTBALL_MATCH_EVENTS, sep=';', index=False)
            print('Saved match events data to disk.')
        
    
    def load_clubs(self, path: Union[str, os.PathLike]) -> pd.DataFrame:
        """Load the dimension table with club information, if it doesn't exist scrape it from Soccerway"""

        if os.path.exists(path):
            df = pd.read_csv(path, sep=';')
            print(f'Loaded file {path} from result.')
            return df
        else:
            import sys
            sys.path.append(os.getcwd())
            sys.path.append(os.path.join(os.getcwd(), 'scraper_soccerway'))
            from scraper_soccerway.gather import extract_clubs_from_html

            url = f"https://nl.soccerway.com/national/netherlands/eredivisie/{FOOTBALL_YEARCODE}/regular-season/{FOOTBALL_COMPETITION_CODE}/tables/"
            print(url)

            clubs = extract_clubs_from_html(url)

            clubs.to_csv(path, sep=';', index=False)

            return clubs

    
    def update_matches(self):
        """Loop through all club URLs and update match dates and match URLs."""

        for _,row in tqdm(self.dim_clubs.iterrows(), total=self.dim_clubs.shape[0]):

            match_url = construct_url(config.URLS['matches'], row['SW_Teamnaam'], row['SW_TeamID'])
            matches_for_club = gather.extract_matches_from_html(match_url)
            self.matches = self.matches.append(matches_for_club)

            time.sleep(config.DEFAULT_SLEEP_S)

        # If a match_id is duplicated, only keep the last entry (most up to date)
        duplicated_mask = self.matches.duplicated(subset=['url_match'], keep='last')
        self.matches = self.matches[~duplicated_mask]

        # Determine match cluster
        self.matches = gather.determine_match_clusters(self.matches)   


    def update_players(self):

        for _,row in tqdm(self.dim_clubs.iterrows(), total=self.dim_clubs.shape[0]):

            match_url = construct_url(config.URLS['teams'], row['SW_Teamnaam'], row['SW_TeamID'])
            players_for_club = gather.extract_squad_from_html(match_url)
            players_for_club['Team'] = row['Team']
            self.dim_players = self.dim_players.append(players_for_club)

            time.sleep(config.DEFAULT_SLEEP_S)

        def check_duplicates(df: pd.DataFrame, diff_col: str = None, keep: str = 'last') -> pd.Series:
            columns = df.columns.drop(diff_col) if diff_col else df.columns
            duplicated_mask = df.duplicated(subset=columns, keep=keep)

            if not diff_col: return duplicated_mask

            if (duplicated_mask.sum() > 0) & (keep == 'last'):
                print(f'Found {duplicated_mask.sum()} changes in column {diff_col}')

                all_duplicates_mask = df.duplicated(subset=columns, keep=False)
                changes = df[all_duplicates_mask].groupby('Naam').agg({diff_col:['first', 'last']})

                for name,row in changes.iterrows():
                    print(f"\t{name:16s}\t{row[diff_col]['first']:>12s}  -->  {row[diff_col]['last']:12s}")              
            return duplicated_mask

        # Remove completely duplicated rows
        duplicated_mask = check_duplicates(self.dim_players)
        self.dim_players = self.dim_players[~duplicated_mask]

        # Check for players that changed position - keep the original row
        duplicated_mask_pos = check_duplicates(self.dim_players, 'Positie', 'first')
        self.dim_players = self.dim_players[~duplicated_mask_pos]

        # Check for players that changed club - keep the new row
        duplicated_mask_team = check_duplicates(self.dim_players, 'Team', 'last')
        self.dim_players = self.dim_players[~duplicated_mask_team]     

        self.dim_players.sort_values(by='SW_ID', inplace=True)
        

    def get_rounds_to_scrape(self) -> list[int]:
        """Return the IDs of the rounds to scrape."""

        rounds_to_scrape= []
        for name, group in self.matches.groupby('Cluster'):
            if all(pd.to_datetime(group['Datum']).dt.date < date.today()):
                # TODO: Add check if round is already scraped 
                rounds_to_scrape.append(name)
            else:
                break
        return rounds_to_scrape


    def process_teammodifications(self, gameweek: int) -> pd.DataFrame:
        """Process substitutions and team checks and append the complete teams to the dataclass."""

        def validate_tactics(teams: pd.DataFrame) -> None:
            for coach, data in teams.groupby('Coach'):
                K = (data['Positie'] == 'K').sum()
                V = (data['Positie'] == 'V').sum()
                M = (data['Positie'] == 'M').sum()
                A = (data['Positie'] == 'A').sum()                       
                tactic = f'{K}{V}{M}{A}'

                if K + V + M + A != 11:
                    print(f'Team of {coach} does not have 11 players.')
                    raise Exception

                elif tactic not in config.ALLOWED_TACTICS:
                    print(f'Team of {coach} plays a tactic that is not allowed: {tactic}')
                    raise Exception

                elif data['Team'].nunique() != 11:
                    p = data.duplicated(subset=['Team'], keep=False)
                    print(f"Team of {coach} has more than 1 player of the same team: {p['Speler'].tolist()}")
                    raise Exception

                else:
                    pass

        teams_new = self.chosen_teams[self.chosen_teams['Speelronde'] == gameweek-1].copy()
        teams_new['Speelronde'] = gameweek

        # Process substitutions
        subs = self.substitutions[self.substitutions['Speelronde']==gameweek].copy()
        for _, row in subs.iterrows():
            sub_mask = (teams_new['Coach']==row['Coach']) & (teams_new['Speler']==row['Wissel_Uit'])
            teams_new.loc[sub_mask, 'Speler'] = row['Wissel_In']
        
        # Join chosen team and dim_players to get info on clubs and positions
        self.dim_players['Naam_fix'] = self.dim_players.apply(lambda x: unidecode(x['Naam']), axis=1)
        players = self.dim_players.set_index('Naam_fix')[['Positie', 'Team', 'Link']]
        teams_new = teams_new.join(players, on='Speler')

        validate_tactics(teams_new)

        return self.chosen_teams.append(teams_new).reset_index(drop=True)


    def process_new_matches(self, gameweek: int):
        """Determine which matches to scrape, perform scraping, store results in DataFrame."""

        all_match_events = pd.DataFrame()

        gameweek_matches = self.matches[self.matches['Cluster'] == gameweek]
        for _,match in tqdm(gameweek_matches.iterrows(), total=gameweek_matches.shape[0]):
            match_events = gather.extract_match_events(match['url_match'], self.dim_players)

            single_match_events = self.match_events.append(match_events).reset_index(drop=True)
            all_match_events = all_match_events.append(single_match_events)
            time.sleep(config.DEFAULT_SLEEP_S)

        return self.match_events.append(all_match_events).reset_index(drop=True)




if __name__ == '__main__':   
    data = CompetitionData()
    # data.update_matches()
    # data.update_players()
    for gameweek in data.get_rounds_to_scrape():
        data.chosen_teams = data.process_teammodifications(gameweek)
        data.match_events = data.process_new_matches(gameweek)

    # print(data.chosen_teams.tail())
    data.save_files_to_results()
