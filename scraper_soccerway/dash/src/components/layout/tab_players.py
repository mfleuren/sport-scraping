from dash import html
import dash_bootstrap_components as dbc

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components.charts_tables import table_all_players

def render(data: DashData, rounds: list[int], clubs: list[str], positions: list[str]) -> html.Div:
    return [
            dbc.Row(
                children=[
                    dbc.Col( 
                        [
                            html.H4("All players overview"),
                            table_all_players.render(data, rounds, clubs, positions)
                        ],
                        md=5,
                        )
                ]
            )
        ]
