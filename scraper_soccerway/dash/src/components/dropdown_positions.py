from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components import ids
from scraper_soccerway.dash.src.components.dropdown_helper import to_dropdown_options

def render(app: Dash, data: DashData) -> html.Div:

    @app.callback(
        Output(ids.POSITION_DROPDOWN, "value"),
        [
            Input(ids.SELECT_ALL_POSITIONS_BUTTON, "n_clicks")
        ]
    )
    def select_all_positions(_: int) -> list[str]:
        return data.all_positions

    return html.Div(
        children=[
            html.H6("Position dropdown"),
            dcc.Dropdown(
                id=ids.POSITION_DROPDOWN,
                options=to_dropdown_options(data.all_positions),
                value=data.all_positions,
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