from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components import ids
from scraper_soccerway.dash.src.components.dropdown_helper import to_dropdown_options

def render(app: Dash, data: DashData) -> html.Div:


    @app.callback(
        Output(ids.COACH_DROPDOWN, "value"),
        [
            Input(ids.SELECT_ALL_COACHES_BUTTON, "n_clicks")
        ]
    )
    def select_all_coaches(_: int) -> list[str]:
        return data.all_coaches

    return html.Div(
        children=[
            html.H6("Coach dropdown"),
            dcc.Dropdown(
                id=ids.COACH_DROPDOWN,
                options=to_dropdown_options(data.all_coaches),
                value=data.all_coaches,
                multi=True,
                placeholder="Choose a coach"
            ),
            html.Button(
                className="dropdown-button",
                children=["Select all"],
                id=ids.SELECT_ALL_COACHES_BUTTON,
                n_clicks=0
            )
        ]
    )