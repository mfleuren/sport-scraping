from dash import Dash, html
import dash_bootstrap_components as dbc

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components import (
    round_dropdown, 
    coach_dropdown, 
    club_dropdown,
    position_dropdown,
    bar_chart, 
    chosen_players_table, 
    all_players_table
    )

def create_layout(app: Dash, data: DashData) -> html.Div:
    """Create the dashboard layout"""

    return html.Div(
        className="app-div",
        children=[
            html.H1(app.title),
            dbc.Row(
                children=[
                    dbc.Col(round_dropdown.render(app, data), md=3),
                    dbc.Col(coach_dropdown.render(app, data), md=3),
                    dbc.Col(club_dropdown.render(app, data), md=3),
                    dbc.Col(position_dropdown.render(app, data), md=3),
                ]
            ),
            dbc.Row(
                children=[
                    dbc.Col(
                        [
                            html.H6("Points by coach overview"),
                            bar_chart.render(app, data)
                        ], 
                        lg=5,
                        width=5
                        ),
                    dbc.Col(
                        [
                            html.H6("Points by chosen player overview"),
                            chosen_players_table.render(app, data)
                        ], 
                        lg=3,
                        width=3
                        ),
                    dbc.Col( 
                        [
                            html.H6("All players overview"),
                            all_players_table.render(app, data)
                        ],
                        lg=3,
                        width=3
                        )
                ]
            )
        ]
    )