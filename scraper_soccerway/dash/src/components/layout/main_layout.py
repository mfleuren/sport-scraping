from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components.dropdowns import (
    dropdown_clubs,
    dropdown_coaches,
    dropdown_positions,
    dropdown_rounds   
)
from scraper_soccerway.dash.src.components.tab_overview import (
    chart_bar_points_by_coach,
    table_all_players,
    table_chosen_players,
    table_substitutions
)

def create_layout(app: Dash, data: DashData) -> html.Div:
    """Create the dashboard layout"""

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
            dbc.Row(
                children=[
                    dbc.Col(
                        [
                            html.H6("Points by coach overview"),
                            chart_bar_points_by_coach.render(app, data)
                        ], 
                        md=5,
                        ),
                    dbc.Col(
                        [
                            html.H6("Substitutions in round"),
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
                            html.H6("Points by chosen player overview"),
                            table_chosen_players.render(app, data)
                        ], 
                        md=5,
                        ),
                    dbc.Col( 
                        [
                            html.H6("All players overview"),
                            table_all_players.render(app, data)
                        ],
                        md=5,
                        )
                ]
            )
        ]
    )