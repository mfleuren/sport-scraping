from dash import html
import dash_bootstrap_components as dbc

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components.charts_tables import (
    table_all_players,
    table_chosen_players,
)


def render(
    data: DashData,
    rounds: list[int],
    coaches: list[str],
    clubs: list[str],
    positions: list[str],
) -> html.Div:
    return [
        dbc.Row(
            children=[
                dbc.Col(
                    [
                        html.H4("Points by chosen player overview"),
                        table_chosen_players.render(data, rounds, coaches),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.H4("All players overview"),
                        table_all_players.render(data, rounds, clubs, positions),
                    ],
                    md=4,
                ),
            ]
        )
    ]
