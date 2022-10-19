from typing import Union
from dataclasses import dataclass, field
from unidecode import unidecode

import os
import time
from datetime import date
from tqdm import tqdm
import pandas as pd
from distutils.util import strtobool

import config, gather, forum_message 
# from utility import forum_robot

from dotenv import load_dotenv
load_dotenv()

MAKE_POST = strtobool(os.getenv('IMGUR_UPLOAD')) and strtobool(os.getenv('FORUM_POST'))

# Football input
FOOTBALL_PATH_INPUT = os.path.join(
    os.getcwd(), 
    'inputs', 
    f"{config.TOURNAMENT_YEAR}_{config.TOURNAMENT_NAME}"
    )
FOOTBALL_PATH_RESULTS = os.path.join(
    os.getcwd(), 
    'results', 
    f"{config.TOURNAMENT_YEAR}_{config.TOURNAMENT_NAME}"
    )

FILE_FOOTBALL_TEAMS_INPUT = os.path.join(FOOTBALL_PATH_INPUT, 'teams.csv')
FILE_FOOTBALL_SUBSTITUTIONS = os.path.join(FOOTBALL_PATH_INPUT, 'substitutions.csv')
FILE_FOOTBALL_FREE_SUBSTITUTIONS = os.path.join(FOOTBALL_PATH_INPUT, 'free_substitutions.csv')
FILE_FOOTBALL_POINTS_SCHEME = os.path.join(FOOTBALL_PATH_INPUT, 'points_scheme.csv')

FILE_FOOTBALL_TEAMS_RESULTS = os.path.join(FOOTBALL_PATH_RESULTS, 'teams.csv')
FILE_FOOTBALL_POINTS_PLAYER = os.path.join(FOOTBALL_PATH_RESULTS, 'points_player.csv')
FILE_FOOTBALL_POINTS_COACH = os.path.join(FOOTBALL_PATH_RESULTS, 'points_coach.csv')
FILE_FOOTBALL_DIM_CLUBS = os.path.join(FOOTBALL_PATH_RESULTS, 'dim_clubs.csv')
FILE_FOOTBALL_DIM_PLAYERS = os.path.join(FOOTBALL_PATH_RESULTS, 'dim_players.csv')
FILE_FOOTBALL_MATCHES = os.path.join(FOOTBALL_PATH_RESULTS, 'matches.csv')
FILE_FOOTBALL_MATCH_EVENTS = os.path.join(FOOTBALL_PATH_RESULTS, 'match_events.csv')

FOOTBALL_YEAR = config.TOURNAMENT_YEAR
FOOTBALL_YEARCODE = str(FOOTBALL_YEAR)
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
        self.points_scheme = pd.read_csv(FILE_FOOTBALL_POINTS_SCHEME, sep=';')
        self.points_player = self.load_file_from_results(FILE_FOOTBALL_POINTS_PLAYER)
        self.points_coach = self.load_file_from_results(FILE_FOOTBALL_POINTS_COACH)
        self.dim_clubs = self.load_clubs(FILE_FOOTBALL_DIM_CLUBS)
        self.dim_players = self.load_file_from_results(FILE_FOOTBALL_DIM_PLAYERS)
        self.matches = self.load_file_from_results(FILE_FOOTBALL_MATCHES)
        self.match_events = self.load_file_from_results(FILE_FOOTBALL_MATCH_EVENTS)

        if strtobool(os.getenv('FOOTBALL_SUBSTITUTIONS')):
            self.substitutions = pd.read_csv(FILE_FOOTBALL_SUBSTITUTIONS, sep=';')
            self.free_substitutions = pd.read_csv(FILE_FOOTBALL_FREE_SUBSTITUTIONS, sep=';')


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

            url = config.URLS['teams']
            print(url)
            clubs = gather.extract_clubs_from_html(url)

            clubs.to_csv(path, sep=';', index=False)

            return clubs

    
    def update_matches(self):
        """Loop through all club URLs and update match dates and match URLs."""

        for _,row in tqdm(self.dim_clubs.iterrows(), total=self.dim_clubs.shape[0]):

            match_url = construct_url(config.URLS['matches'], row['SW_Teamnaam'], row['SW_TeamID'])
            matches_for_club = gather.extract_matches_from_html(match_url)
            self.matches = pd.concat([self.matches, matches_for_club], ignore_index=True)

            time.sleep(config.DEFAULT_SLEEP_S)

        # If a match_id is duplicated, only keep the last entry (most up to date)
        duplicated_mask = self.matches.duplicated(subset=['url_match'], keep='last')
        self.matches = self.matches[~duplicated_mask]

        # Determine match cluster
        self.matches = gather.determine_match_clusters(self.matches)   


    def update_players(self):

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

        all_players = self.dim_players.copy()
        for _,row in tqdm(self.dim_clubs.iterrows(), total=self.dim_clubs.shape[0]):

            match_url = construct_url(config.URLS['teams'], row['SW_Teamnaam'], row['SW_TeamID'])
            players_for_club = gather.extract_squad_from_html(match_url)
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

        self.dim_players = all_players.sort_values(by='SW_ID')
        

    def get_rounds_to_scrape(self) -> list[int]:
        """Return the IDs of the rounds to scrape."""

        rounds_to_scrape= []
        for name, group in self.matches.groupby('Cluster'):
            rounds_already_processed = self.points_coach['Speelronde'].unique().tolist()

            if all(pd.to_datetime(group['Datum']).dt.date <= date.today()) &\
                (group.iloc[0]['Cluster'] not in rounds_already_processed):               

                rounds_to_scrape.append(name)
            else:
                continue
        return rounds_to_scrape


    def process_teammodifications(self, gameweek: int) -> pd.DataFrame:
        """Process substitutions and team checks and append the complete teams to the dataclass."""

        def validate_tactics(teams: pd.DataFrame) -> None:
            for coach, data in teams.groupby('Coach'):
                K = (data['Positie'] == 'K').sum()
                V = (data['Positie'] == 'V').sum()
                M = (data['Positie'] == 'M').sum()
                A = (data['Positie'] == 'A').sum()
                special = data['Speler'].str.contains('!').sum()                       
                tactic = f'{K}{V}{M}{A}'

                if K + V + M + A + special != 11:
                    print(data)
                    print(f'Team of {coach} does not have 11 players.')
                    raise Exception

                elif tactic not in config.ALLOWED_TACTICS and special == 0:
                    print(data)
                    print(f'Team of {coach} plays a tactic that is not allowed: {tactic}')
                    raise Exception

                elif data['Team'].nunique() != 11 and special == 0:
                    p = data.duplicated(subset=['Team'], keep=False)
                    print(special)
                    print(data[['Speler', 'Team']])
                    print(f"Team of {coach} has more than 1 player of the same team: {p['Speler'].tolist()}")
                    raise Exception

                else:
                    pass

        teams_new = self.chosen_teams[self.chosen_teams['Speelronde'] == gameweek-1].copy()
        teams_new['Speelronde'] = gameweek
        if 'Positie' in teams_new.columns:
            teams_new.drop(['Positie', 'Team', 'Link'], axis=1, inplace=True)

        # Process substitutions
        subs = self.substitutions[self.substitutions['Speelronde']==gameweek].copy()
        if subs.shape[0] > 0:
            print(f"Processed substitutions, speelronde {gameweek}:")
        for _, row in subs.iterrows():
            sub_mask = (teams_new['Coach']==row['Coach']) & (teams_new['Speler']==row['Wissel_Uit'])
            teams_new.loc[sub_mask, 'Speler'] = row['Wissel_In']
            print(f"{row['Coach']} [{row['Wissel_Uit']} --> {row['Wissel_In']}]")

        # Process free substitutions
        subs = self.free_substitutions[self.free_substitutions['Speelronde']==gameweek].copy()
        if subs.shape[0] > 0:
            print(f"Processed free substitutions, speelronde {gameweek}:")
        for _, row in subs.iterrows():
            sub_mask = (teams_new['Coach']==row['Coach']) & (teams_new['Speler']==row['Wissel_Uit'])
            teams_new.loc[sub_mask, 'Speler'] = row['Wissel_In']
            print(f"{row['Coach']} [{row['Wissel_Uit']} --> {row['Wissel_In']}]")
        
        # Join chosen team and dim_players to get info on clubs and positions
        self.dim_players['Naam_fix'] = self.dim_players.apply(lambda x: unidecode(x['Naam']), axis=1)
        players = self.dim_players.set_index('Naam_fix')[['Positie', 'Team', 'Link']].copy()
        teams_new = teams_new.join(players, on='Speler')

        validate_tactics(teams_new)

        return pd.concat([self.chosen_teams, teams_new], ignore_index=True)


    def process_new_matches(self, gameweek: int) -> pd.DataFrame:
        """Determine which matches to scrape, perform scraping, store results in DataFrame."""

        all_match_events = pd.DataFrame()

        gameweek_matches = self.matches[self.matches['Cluster'] == gameweek].copy()
        for _,match in tqdm(gameweek_matches.iterrows(), total=gameweek_matches.shape[0]):
            match_events = gather.extract_match_events(match['url_match'], self.dim_players.copy())
            all_match_events = pd.concat([all_match_events, match_events], ignore_index=True)
            time.sleep(config.DEFAULT_SLEEP_S)
        all_match_events['Speelronde'] = gameweek

        return pd.concat([self.match_events, all_match_events], ignore_index=True)


    def calculate_point_by_player(self, gameweek: int) -> pd.DataFrame:
        """Perform points calculations"""

        all_events = self.match_events.copy()
        events = all_events[all_events['Speelronde']==gameweek]
        player = self.dim_players.copy()
        events_player = events.join(player[['Link', 'Positie']].set_index('Link'), on='Link')
        points_scheme = self.points_scheme.copy().set_index('Positie')
        points_player = events_player.join(points_scheme, on='Positie', lsuffix='_e', rsuffix='_p')

        points_player[['Wedstrijd_Gewonnen_e', 'Wedstrijd_Gelijk_e', 'Wedstrijd_Verloren_e', 'CleanSheet_e']] = \
            points_player[['Wedstrijd_Gewonnen_e', 'Wedstrijd_Gelijk_e', 'Wedstrijd_Verloren_e', 'CleanSheet_e']].astype('bool') 
        
        points_player['P_Gespeeld'] = points_player['Wedstrijd_Gespeeld'] * (points_player['Minuten_Gespeeld']/90)
        points_player['P_Gewonnen'] = points_player['Wedstrijd_Gewonnen_p'] * (points_player['Minuten_Gespeeld']/90) * points_player['Wedstrijd_Gewonnen_e']
        points_player['P_Gelijk'] = points_player['Wedstrijd_Gelijk_p'] * (points_player['Minuten_Gespeeld']/90) * points_player['Wedstrijd_Gelijk_e']
        points_player['P_Verloren'] = points_player['Wedstrijd_Verloren_p'] * (points_player['Minuten_Gespeeld']/90) * points_player['Wedstrijd_Verloren_e']
        points_player['P_Kaart_Geel'] = points_player['Kaart_Geel_p'] * points_player['Kaart_Geel_e']
        points_player['P_Kaart_Rood'] = points_player['Kaart_Rood_p'] * points_player['Kaart_Rood_e']
        points_player['P_Doelpunt'] = points_player['Doelpunt'] * points_player['Goal']
        points_player['P_Assist'] = points_player['Assist_p'] * points_player['Assist_e']
        points_player['P_Tegendoelpunt'] = points_player['Tegendoelpunt_p'] * points_player['Tegendoelpunt_e']
        points_player['P_Eigen_Doelpunt'] = points_player['Eigen_Doelpunt'] * points_player['Goal_Eigen']
        points_player['P_Clean_Sheet'] = points_player['CleanSheet_p'] * points_player['CleanSheet_e']
        points_player['P_Penalty_Gescoord'] = points_player['Penalty_Gescoord'] * points_player['Penalty_Goal']
        points_player['P_Penalty_Gemist'] = points_player['Penalty_Gemist_p'] * points_player['Penalty_Gemist_e']
        points_player['P_Penalty_Gestopt'] = points_player['Penalty_Gestopt_p'] * points_player['Penalty_Gestopt_e']

        cols_to_keep = ['Speler', 'Link'] + points_player.columns[points_player.columns.str.contains('P_')].tolist()
        cols_to_drop = points_player.columns[~points_player.columns.isin(cols_to_keep)]
        points_player.drop(cols_to_drop, axis=1, inplace=True)
        points_player['P_Totaal'] = points_player.drop(['Speler', 'Link'], axis=1).sum(axis=1)
        points_player['Speelronde'] = gameweek

        return pd.concat([self.points_player, points_player], ignore_index=True)


    def calculate_points_by_coach(self, gameweek: int) -> pd.DataFrame:
        """Calculate points by coach"""

        points_player_all = self.points_player.copy()
        chosen_teams_all = self.chosen_teams.copy()

        points_player = points_player_all[points_player_all['Speelronde']==gameweek]
        coach_teams = chosen_teams_all[chosen_teams_all['Speelronde']==gameweek]

        cols_to_drop = points_player.columns[~points_player.columns.isin(['Link', 'P_Totaal'])]
        coach_teams = coach_teams.join(points_player.drop(cols_to_drop, axis=1).set_index('Link'), on='Link')
        
        return pd.concat([self.points_coach, coach_teams], ignore_index=True)


def create_message_and_post(data: CompetitionData, gameweeks: list[int]) -> None:
    """Process the data and generate a message to post on a internet forum."""

    message = forum_message.Message(gameweeks=gameweeks)
    message.create_substitutions_table(data.substitutions.copy())
    message.create_round_ranking(data.points_coach.copy())
    message.create_general_ranking(data.points_coach.copy(), data.substitutions.copy())
    message.create_teams_overview(data.chosen_teams.copy())
    message.create_players_overview(data.dim_players.copy())

    single_message = []
    for idx,_ in enumerate(gameweeks):
        single_message.append(message.substitution_table[idx])
        single_message.append(message.round_ranking[idx])
    single_message.append(message.general_ranking)
    single_message.append(message.teams_overview)
    single_message.append(message.players_overview)

    final_message = ''.join(single_message)
    
    if MAKE_POST:
        forum_robot.post_results_to_forum(final_message)


def soccerway_scraper():
    """Perform a round in the soccerway scraper"""

    data = CompetitionData()
    data.update_matches()
    data.update_players()
    rounds_to_scrape = data.get_rounds_to_scrape()
    for gameweek in rounds_to_scrape:
        print(f'Scraping round {gameweek}')
        data.chosen_teams = data.process_teammodifications(gameweek)
        data.match_events = data.process_new_matches(gameweek)
        data.points_player = data.calculate_point_by_player(gameweek)
        data.points_coach = data.calculate_points_by_coach(gameweek)

    if len(rounds_to_scrape) > 0:
        create_message_and_post(data, rounds_to_scrape)
        data.save_files_to_results()


if __name__ == '__main__':   
    soccerway_scraper()

# TODO: Add points to chosen teams message