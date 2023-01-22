from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd

from . import ids
from .dropdown_helper import to_dropdown_options

def render(app: Dash, data: pd.DataFrame) -> html.Div:

    @app.callback(
        Output(ids.ROUND_DROPDOWN, "value"),
        [
            Input(ids.SELECT_ROUNDS_DROPDOWN_CHOICE, "value"),
        ]
    )
    def select_rounds(value: str) -> list[str]:
        print(f"Radio button value: {value}")

        if value == "Select Last":
            return [data["Speelronde"].max()]
        elif value == "Select All":
            return data["Speelronde"].unique().tolist()
        
    rounds = data["Speelronde"].unique()

    return html.Div(
        children=[
            html.H6("Round dropdown"),
            dcc.Dropdown(
                id=ids.ROUND_DROPDOWN,
                options=to_dropdown_options(rounds),
                value=rounds,
                multi=True,
                placeholder="Choose a round"
            ),
            dcc.RadioItems(
                id=ids.SELECT_ROUNDS_DROPDOWN_CHOICE,
                options=["Select All", "Select Last", "Select Custom"],
                value="Select Last"
            )
        ]
    )