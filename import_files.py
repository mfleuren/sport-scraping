import pandas as pd
import pathlib
from typing import Union

def import_teams(path: Union[str, pathlib.Path]):
    return pd.read_csv(path, sep=';')

def import_matches(path: Union[str, pathlib.Path]):
    return pd.read_csv(path, sep=';')

def import_points(path: Union[str, pathlib.Path]):
    return pd.read_csv(path, sep=';')

