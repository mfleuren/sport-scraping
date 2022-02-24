from typing import Union, Tuple
import pandas as pd

import os
import pathlib



def import_teams(path: Union[str, pathlib.Path]):
    return pd.read_csv(path, sep=';')

def import_matches(path: Union[str, pathlib.Path]):
    matches = pd.read_csv(path, sep=';')
    matches['MATCH_DATE'] = pd.to_datetime(matches['MATCH_DATE'], format='%d-%m-%Y')
    return matches

def import_points(path: Union[str, pathlib.Path]):
    return pd.read_csv(path, sep=';')

def load_csv_files(path_csv_files: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    path_csv_teams = os.path.join(path_csv_files, 'teams.csv')
    path_csv_matches = os.path.join(path_csv_files, 'matches.csv')
    path_csv_points = os.path.join(path_csv_files, 'points.csv')

    # Load CSV-files with teams, match and points information
    df_teams = import_teams(path_csv_teams)
    df_matches = import_matches(path_csv_matches)
    df_points = import_points(path_csv_points)

    return df_teams, df_matches, df_points

