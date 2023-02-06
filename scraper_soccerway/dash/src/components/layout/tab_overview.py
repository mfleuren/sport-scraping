from dash import html
import dash_bootstrap_components as dbc

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components.charts_tables import (
    chart_bar_points_by_coach,
    chart_bar_wins_by_coach,
    table_substitutions,
)
from scraper_soccerway.dash.src.components.dropdowns.dropdown_rounds import rounds_to_str


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
                        html.H4(f"Points by coach overview for round(s)"),
                        chart_bar_points_by_coach.render(data, rounds, coaches),
                    ],
                    md=5,
                ),
                dbc.Col(
                    [
                        html.H4(f"Substitutions in round(s)"),
                        table_substitutions.render(data, rounds, coaches),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.H4(f"Wins by coach (until round {max(rounds)})"),
                        chart_bar_wins_by_coach.render(data, rounds, coaches),
                    ],
                    md=3,
                ),
            ],
        )
    ]
