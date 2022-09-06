from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd

from . import ids

data = pd.read_csv('.\\.\\results\\2022_Eredivisie\\points_coach.csv', sep=';')

def render(app: Dash) -> html.Div:
    
    all_rounds = data['Speelronde'].unique()

    @app.callback(
        Output(ids.ROUND_DROPDOWN, "value"),
        Input(ids.SELECT_ALL_ROUNDS_BUTTON, "n_clicks"),
    )
    def select_all_rounds(_: int) -> list[int]:
        return all_rounds

    return html.Div(
        children=[
            html.H6("Round"),
            dcc.Dropdown(
                id=ids.ROUND_DROPDOWN,
                options=[{"label":rnd, "value":rnd} for rnd in all_rounds],
                value=all_rounds,
                multi=True,
            ),
            html.Button(
                className="dropdown-button",
                children=["Select All"],
                id=ids.SELECT_ALL_ROUNDS_BUTTON,
                n_clicks=0
            )
        ]
    )