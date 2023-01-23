from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd

from . import ids
from .dropdown_helper import to_dropdown_options

def render(app: Dash, data: pd.DataFrame) -> html.Div:

    @app.callback(
        Output(ids.POSITION_DROPDOWN, "value"),
        [
            Input(ids.SELECT_ALL_POSITIONS_BUTTON, "n_clicks")
        ]
    )
    def select_all_positions(_: int) -> list[str]:
        return data["Positie"].unique().tolist()

    positions = data["Positie"].unique()

    return html.Div(
        children=[
            html.H6("Position dropdown"),
            dcc.Dropdown(
                id=ids.POSITION_DROPDOWN,
                options=to_dropdown_options(positions),
                value=positions,
                multi=True,
                placeholder="Choose a position"
            ),
            html.Button(
                className="dropdown-button",
                children=["Select all"],
                id=ids.SELECT_ALL_POSITIONS_BUTTON,
                n_clicks=0
            )
        ]
    )