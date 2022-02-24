import pandas as pd
import pathlib
from typing import Union

def import_teams(path: Union[str, pathlib.Path]):
    return pd.read_csv(path, sep=';')

teams = import_teams('2022_voorjaar/teams.csv')