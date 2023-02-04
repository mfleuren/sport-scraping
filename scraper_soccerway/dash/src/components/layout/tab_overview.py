from dash import Dash, html
import dash_bootstrap_components as dbc

from scraper_soccerway.dash.src.components import ids
from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components.charts_tables import (
    chart_bar_points_by_coach,
    table_all_players,
    table_chosen_players,
    table_substitutions
)

def create_tab_overview(app: Dash, data: DashData) -> html.Div:
    return [
            dbc.Row(
                children=[
                    dbc.Col(
                        [
                            html.H4("Test"),
                            html.H4("Points by coach overview"),
                            html.Div(id=ids.BAR_CHART, children=chart_bar_points_by_coach.render(app, data)),
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
