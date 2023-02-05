from dash import html
import dash_bootstrap_components as dbc

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components.charts_tables import (
    chart_bar_points_by_coach,
    table_chosen_players,
    table_substitutions,
)


def render(
    data: DashData,
    rounds: list[int],
    coaches: list[str],
) -> html.Div:
    return [
        dbc.Row(
            children=[
                dbc.Col(
                    [
                        html.H4("Points by coach overview"),
                        chart_bar_points_by_coach.render(data, rounds, coaches),
                    ],
                    md=5,
                ),
                dbc.Col(
                    [
                        html.H4("Substitutions in round"),
                        table_substitutions.render(data, rounds, coaches),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.H4("Points by chosen player overview"),
                        table_chosen_players.render(data, rounds, coaches),
                    ],
                    md=3,
                ),
            ],
        )
    ]
