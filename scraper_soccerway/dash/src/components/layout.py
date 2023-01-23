from dash import Dash, html
import dash_bootstrap_components as dbc
import pandas as pd

from src.components import (
    round_dropdown, 
    coach_dropdown, 
    club_dropdown,
    position_dropdown,
    bar_chart, 
    chosen_players_table, 
    all_players_table
    )

def create_layout(app: Dash, teams_data: pd.DataFrame, players_data: pd.DataFrame) -> html.Div:
    """Create the dashboard layout"""

    return html.Div(
        className="app-div",
        children=[
            html.H1(app.title),
            dbc.Row(
                children=[
                    dbc.Col(round_dropdown.render(app, teams_data)),
                    dbc.Col(coach_dropdown.render(app, teams_data)),
                    dbc.Col(club_dropdown.render(app, players_data)),
                    dbc.Col(position_dropdown.render(app, players_data)),
                ]
            ),
            dbc.Row(
                children=[
                    dbc.Col(
                        [
                            html.H6("Points by coach overview"),
                            bar_chart.render(app, teams_data)
                        ], 
                        width=5
                        ),
                    dbc.Col(
                        [
                            html.H6("Points by chosen player overview"),
                            chosen_players_table.render(app, teams_data)
                        ], 
                        width=3
                        ),
                    dbc.Col( 
                        [
                            html.H6("All players overview"),
                            all_players_table.render(app, players_data)
                        ],
                        width=3
                        )
                ]
            )
        ]
    )