from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components import ids
from scraper_soccerway.dash.src.components.dropdowns.dropdown_helper import to_dropdown_options

def render(app: Dash, data: DashData) -> html.Div:

    @app.callback(
        Output(ids.ROUND_DROPDOWN, "value"),
        [
            Input(ids.SELECT_ROUNDS_DROPDOWN_CHOICE, "value"),
        ]
    )
    def select_rounds(value: str) -> list[str]:
        print(f"Radio button value: {value}")

        if value == "Select Last":
            return [data.max_round]
        elif value == "Select All":
            return data.all_rounds
        
    return html.Div(
        children=[
            html.H4("Round dropdown"),
            dcc.Dropdown(
                id=ids.ROUND_DROPDOWN,
                options=to_dropdown_options(data.all_rounds),
                value=data.all_rounds,
                multi=True,
                placeholder="Choose a round"
            ),
            dcc.RadioItems(
                id=ids.SELECT_ROUNDS_DROPDOWN_CHOICE,
                options=["Select All", "Select Last"],
                value="Select Last"
            )
        ]
    )