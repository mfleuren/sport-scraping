from dash import Dash, html
import dash_bootstrap_components as dbc
import pandas as pd

from src.components import round_dropdown, coach_dropdown, bar_chart, data_table

def create_layout(app: Dash, data: pd.DataFrame) -> html.Div:
    """Create the dashboard layout"""

    return html.Div(
        className="app-div",
        children=[
            html.H1(app.title),
            dbc.Row(
                children=[
                    dbc.Col(round_dropdown.render(app, data)),
                    dbc.Col(coach_dropdown.render(app, data))
                ]
            ),
            dbc.Row(
                children=[
                    dbc.Col(bar_chart.render(app, data), width=5),
                    dbc.Col(data_table.render(app, data), width=3)
                ]
            )
        ]
    )