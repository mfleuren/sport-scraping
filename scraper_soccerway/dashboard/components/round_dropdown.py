from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np

from . import ids

data = pd.read_csv('.\\.\\results\\2022_Eredivisie\\points_coach.csv', sep=';')

def render(app: Dash) -> html.Div:
    
    all_rounds = data['Speelronde'].unique()

    return html.Div(
        children=[
            html.H6("Round"),
            dcc.Dropdown(
                id=ids.ROUND_DROPDOWN,
                options=[{"label":rnd, "value":rnd} for rnd in all_rounds],
                value=np.max(all_rounds),
                multi=False,
            )
        ]
    )