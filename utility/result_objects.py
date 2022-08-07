from dataclasses import dataclass, field
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from typing import Union

"""
SET CONSTANTS
"""

load_dotenv()
# Cycling input
PATH_INPUT = os.path.join(
    os.getcwd(), 
    'inputs', 
    f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}"
    )
PATH_RESULTS = os.path.join(
    os.getcwd(), 'results', 
    f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}"
    )

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
FILE_FOOTBALL_TEAMS_RESULTS = os.path.join(FOOTBALL_PATH_RESULTS, 'teams.csv')
FILE_FOOTBALL_SUBSTITUTIONS = os.path.join(FOOTBALL_PATH_INPUT, 'substitutions.csv')
FILE_FOOTBALL_POINTS_SCHEME = os.path.join(FOOTBALL_PATH_INPUT, 'points_scheme.csv')


"""
DATACLASSES FOR CYCLING SCRAPERS
"""

@dataclass
class Message:
    img_urls: list[str] = field(default_factory=list)
    coach_mentions: list[list[str]] = field(default_factory=list)
    summary_img_urls: list[str] = field(default_factory=list)


@dataclass
class StageResults:
    matches: pd.DataFrame = field(init=False)
    default_points: pd.DataFrame = field(init=False)
    teams: pd.DataFrame = field(init=False)
    all_results: pd.DataFrame = field(init=False)
    all_points: pd.DataFrame = field(init=False)
    stage_results: list[pd.DataFrame] = field(default_factory=list)
    stage_points: list[pd.DataFrame] = field(default_factory=list)
    stage_standings: list[pd.DataFrame] = field(default_factory=list)

    
    def __post_init__(self):
        self.matches = pd.read_csv(os.path.join(PATH_INPUT, os.getenv('FILENAME_MATCHES')), sep=';')
        self.matches['MATCH_DATE'] = pd.to_datetime(self.matches['MATCH_DATE'], format='%d-%m-%Y')

        self.teams = pd.read_csv(os.path.join(PATH_INPUT, os.getenv('FILENAME_TEAMS')), sep=';', encoding='latin-1')
        if not any(['ROUND_IN', 'ROUND_OUT']) in self.teams.columns:
            self.teams['ROUND_IN'] = np.where(self.teams['POSITION'] == 'In',1, np.nan)
            self.teams['ROUND_OUT'] = np.nan

        self.default_points = pd.read_csv(os.path.join(PATH_INPUT, os.getenv('FILENAME_POINTS')), sep=';')      

        if os.path.exists(os.path.join(PATH_RESULTS, os.getenv('FILENAME_ALL_RESULTS'))):
            self.all_results = pd.read_csv(os.path.join(PATH_RESULTS, os.getenv('FILENAME_ALL_RESULTS')))
            print(f'Loaded all_results file, dataframe shape: {self.all_results.shape}')
        else:
            self.all_results = pd.DataFrame(columns=['MATCH'])
            print('Previous results not found. Pre-allocated empty dataframe for all_results')

        if os.path.exists(os.path.join(PATH_RESULTS, os.getenv('FILENAME_ALL_POINTS'))):
            self.all_points = pd.read_csv(os.path.join(PATH_RESULTS, os.getenv('FILENAME_ALL_POINTS'))
                )
            print(f'Loaded all_points file, dataframe shape: {self.all_points.shape}')
        else:
            self.all_points = pd.DataFrame(columns=['MATCH'])
            print('Previous points not found. Pre-allocated empty dataframe for all_points')


    def export_concatenated_data(self) -> None:
        self.all_results.to_csv(
            os.path.join(PATH_RESULTS, os.getenv('FILENAME_ALL_RESULTS')), 
            index=False
            )
        self.all_points.to_csv(
            os.path.join(PATH_RESULTS, os.getenv('FILENAME_ALL_POINTS')), 
            index=False
            )


    def export_teams(self) -> None:
        self.teams.to_csv(
            os.path.join(PATH_INPUT, os.getenv('FILENAME_TEAMS')), 
            index=False
        )
        

    def append_stages_to_existing_data(self):
        self.all_results = pd.concat([self.all_results, pd.concat(self.stage_results)], ignore_index=True)
        self.all_points = pd.concat([self.all_points, pd.concat(self.stage_points)], ignore_index=True)


"""
DATACLASSES FOR FOOTBALL SCRAPERS
"""

@dataclass
class CompetitionData:
    chosen_teams: pd.DataFrame = field(init=False)
    substitutions: pd.DataFrame = field(init=False)
    points_scheme: pd.DataFrame = field(init=False)

    

    def __post_init__(self):
        self.chosen_teams = self.load_file_from_input_or_results(FILE_FOOTBALL_TEAMS_INPUT, FILE_FOOTBALL_TEAMS_RESULTS)
        self.substitutions = pd.read_csv(FILE_FOOTBALL_SUBSTITUTIONS, sep=';')
        self.points_scheme = pd.read_csv(FILE_FOOTBALL_POINTS_SCHEME, sep=';')


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

        

if __name__ == '__main__':
    data = CompetitionData()
    print(data.points_scheme.columns)

