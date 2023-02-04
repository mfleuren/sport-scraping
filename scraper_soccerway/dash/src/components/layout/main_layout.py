from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from scraper_soccerway.dash.src.components import ids
from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components.dropdowns import (
    dropdown_clubs,
    dropdown_coaches,
    dropdown_positions,
    dropdown_rounds   
)
from scraper_soccerway.dash.src.components.charts_tables import (
    chart_bar_points_by_coach,
    table_all_players,
    table_chosen_players,
    table_substitutions
)

def create_layout(app: Dash, data: DashData) -> html.Div:
    """Create the dashboard layout"""

    @app.callback(
        Output(ids.TAB_CONTENT, 'children'),
        [
            Input(ids.TABS_OBJECT, 'value'),
            Input(ids.ROUND_DROPDOWN, "value"),
            Input(ids.COACH_DROPDOWN, "value"),
            Input(ids.CLUB_DROPDOWN, "value"),
            Input(ids.POSITION_DROPDOWN, "value")
        ]
        )
    def update_tab_content(tab: str, rounds: list[int], coaches: list[str], clubs: list[str], positions: list[str]) -> list[html.Div]:

        if tab == ids.TAB_OVERVIEW: 
            print("In Overview tab")
            bar_chart = chart_bar_points_by_coach.render(app, data)
            print(bar_chart)
            return [
            dbc.Row(
                id=ids.BAR_CHART,
                children=[
                    dbc.Col(
                        [
                            html.H4("Test"),
                            html.H4("Points by coach overview"),
                            bar_chart,
                            html.H4("Test"),
                        ], 
                        md=5,
                        ),
                    dbc.Col(
                        [
                            html.H4("Substitutions in round"),
                            table_substitutions.render(app, data)
                        ],
                        md=3
                        ),                            
                ]
            ),
            dbc.Row(
                children=[
                    dbc.Col(
                        [
                            html.H4("Points by chosen player overview"),
                            table_chosen_players.render(app, data)
                        ], 
                        md=5,
                        ),
                    dbc.Col( 
                        [
                            html.H4("All players overview"),
                            table_all_players.render(app, data)
                        ],
                        md=5,
                        )
                ]
            )
        ]
        else:
            print("In other tab")
            return html.Div("Under construction.")

    return html.Div(
        className="app-div",
        children=[
            html.H1(app.title),
            dbc.Row(
                children=[
                    dbc.Col(dropdown_rounds.render(app, data), md=3),
                    dbc.Col(dropdown_coaches.render(app, data), md=3),
                    dbc.Col(dropdown_clubs.render(app, data), md=3),
                    dbc.Col(dropdown_positions.render(app, data), md=3),
                ]
            ),
            dcc.Tabs(
                id=ids.TABS_OBJECT,
                value=ids.TAB_OVERVIEW,
                children=[
                    dcc.Tab(label="Score overview", value=ids.TAB_OVERVIEW),
                    dcc.Tab(label="Team of the Week", value=ids.TAB_TEAM_WEEK),
                ]
            ), 
            dbc.Row(
                id=ids.TAB_CONTENT
            )
        ]
    )