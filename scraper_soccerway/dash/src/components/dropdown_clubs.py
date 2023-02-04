from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components import ids
from scraper_soccerway.dash.src.components.dropdown_helper import to_dropdown_options

def render(app: Dash, data: DashData) -> html.Div:

    @app.callback(
        Output(ids.CLUB_DROPDOWN, "value"),
        [
            Input(ids.SELECT_ALL_CLUBS_BUTTON, "n_clicks")
        ]
    )
    def select_all_clubs(_: int) -> list[str]:
        return data.all_clubs

    return html.Div(
        children=[
            html.H6("Club dropdown"),
            dcc.Dropdown(
                id=ids.CLUB_DROPDOWN,
                options=to_dropdown_options(data.all_clubs),
                value=data.all_clubs,
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