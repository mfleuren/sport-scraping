from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd

from . import ids

def render(data: pd.DataFrame) -> html.Div:

    rounds = data["Speelronde"].unique()

    return html.Div(
        children=[
            html.H6("Round dropdown"),
            dcc.Dropdown(
                id=ids.ROUND_DROPDOWN,
                options=rounds,
                multi=False,
                placeholder="Choose a round"
            )
        ]
    )