from typing import Union, Tuple
import pandas as pd

import os
import pathlib



def import_teams(path: Union[str, pathlib.Path]):
    return pd.read_csv(path, sep=';')

def import_matches(path: Union[str, pathlib.Path]):
    return pd.read_csv(path, sep=';')

def import_points(path: Union[str, pathlib.Path]):
    return pd.read_csv(path, sep=';')

def load_csv_files(competition_year_name: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    PATH_CSV_FILES = os.path.join(os.path.dirname(os.path.realpath(__file__)), competition_year_name) 
    PATH_CSV_TEAMS = os.path.join(PATH_CSV_FILES, 'teams.csv')
    PATH_CSV_MATCHES = os.path.join(PATH_CSV_FILES, 'matches.csv')
    PATH_CSV_POINTS = os.path.join(PATH_CSV_FILES, 'points.csv')

    # Load CSV-files with teams, match and points information
    df_teams = import_teams(PATH_CSV_TEAMS)
    df_matches = import_matches(PATH_CSV_MATCHES)
    df_points = import_points(PATH_CSV_POINTS)

    return df_teams, df_matches, df_points

