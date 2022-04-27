from typing import Tuple
import pandas as pd
import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

FILENAME_TEAMS = 'teams.csv'
FILENAME_MATCHES = 'matches.csv'
FILENAME_POINTS = 'points.csv'
FILENAME_ALL_RESULTS = 'all_results.csv'

PATH_INPUT = os.path.join(os.getcwd(), 'inputs', f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}")
PATH_RESULTS = os.path.join(os.getcwd(), 'results', f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}")
PATH_TEAMS = os.path.join(PATH_INPUT, FILENAME_TEAMS)
PATH_MATCHES = os.path.join(PATH_INPUT, FILENAME_MATCHES)
PATH_POINTS = os.path.join(PATH_INPUT, FILENAME_POINTS)
PATH_ALL_RESULTS = os.path.join(PATH_RESULTS, FILENAME_ALL_RESULTS)


def import_matches(path: pathlib.Path):
    """Load matches data from CSV, convert date to datetime format."""
    matches = pd.read_csv(path, sep=';')
    matches['MATCH_DATE'] = pd.to_datetime(matches['MATCH_DATE'], format='%d-%m-%Y')
    return matches


def load_csv_files() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    teams = pd.read_csv(PATH_TEAMS, sep=';')
    points = pd.read_csv(PATH_POINTS, sep=';')
    matches = import_matches(PATH_MATCHES)    

    if os.path.exists(PATH_ALL_RESULTS):
        all_results = pd.read_csv(PATH_ALL_RESULTS)
        print(f'Loaded all_results file, dataframe shape: {all_results.shape}')
    else:
        all_results = pd.DataFrame(columns=['MATCH'])
        print('Previous results not found. Pre-allocated empty dataframe for all_results')

    return teams, matches, points, all_results

