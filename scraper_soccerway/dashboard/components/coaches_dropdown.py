from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np

from . import ids


def render(app: Dash, data: pd.DataFrame) -> html.Div:
    
    all_coaches = data['Coach'].unique()

    @app.callback(
        Output(ids.COACHES_DROPDOWN, "value"),
        Input(ids.SELECT_ALL_COACHES_BUTTON, "n_clicks"),
    )
    def select_all_coaches(_: int) -> list[str]:
        return all_coaches

    return html.Div(
        children=[
            html.H6("Coach(es)"),
            dcc.Dropdown(
                id=ids.COACHES_DROPDOWN,
                options=[{"label":coach, "value":coach} for coach in all_coaches],
                value=all_coaches,
                multi=True,
            ),
            html.Button(
                className="dropdown-button",
                children=["Select All"],
                id=ids.SELECT_ALL_COACHES_BUTTON,
                n_clicks=0,
            )
        ]
    )