import pandas as pd
import os
from dotenv import load_dotenv


load_dotenv()

FILENAME_TEAMS = 'teams.csv'
FILENAME_MATCHES = 'matches.csv'
FILENAME_POINTS = 'points.csv'
FILENAME_ALL_RESULTS = 'all_results.csv'

PATH_INPUT = os.path.join(os.getcwd(), 'inputs', f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}")
PATH_RESULTS = os.path.join(os.getcwd(), 'results', f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}")


def import_matches() -> pd.DataFrame:
    """Load matches data from CSV, convert date to datetime format."""
    matches = pd.read_csv(os.path.join(PATH_INPUT, FILENAME_MATCHES), sep=';')
    matches['MATCH_DATE'] = pd.to_datetime(matches['MATCH_DATE'], format='%d-%m-%Y')
    return matches


def import_teams() -> pd.DataFrame:
    return pd.read_csv(os.path.join(PATH_INPUT, FILENAME_TEAMS), sep=';')


def import_points() -> pd.DataFrame:
    return pd.read_csv(os.path.join(PATH_INPUT, FILENAME_POINTS), sep=';')


def import_all_results() -> pd.DataFrame:
    if os.path.exists(os.path.join(PATH_RESULTS, FILENAME_ALL_RESULTS)):
        all_results = pd.read_csv(os.path.join(PATH_RESULTS, FILENAME_ALL_RESULTS))
        print(f'Loaded all_results file, dataframe shape: {all_results.shape}')
    else:
        all_results = pd.DataFrame(columns=['MATCH'])
        print('Previous results not found. Pre-allocated empty dataframe for all_results')
    return all_results