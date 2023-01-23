from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd

from . import ids
from .dropdown_helper import to_dropdown_options

def render(app: Dash, data: pd.DataFrame) -> html.Div:

    @app.callback(
        Output(ids.CLUB_DROPDOWN, "value"),
        [
            Input(ids.SELECT_ALL_CLUBS_BUTTON, "n_clicks")
        ]
    )
    def select_all_clubs(_: int) -> list[str]:
        return data["Team"].unique().tolist()

    clubs = data["Team"].unique()

    return html.Div(
        children=[
            html.H6("Club dropdown"),
            dcc.Dropdown(
                id=ids.CLUB_DROPDOWN,
                options=to_dropdown_options(clubs),
                value=clubs,
                multi=True,
                placeholder="Choose a club"
            ),
            html.Button(
                className="dropdown-button",
                children=["Select all"],
                id=ids.SELECT_ALL_CLUBS_BUTTON,
                n_clicks=0
            )
        ]
    )