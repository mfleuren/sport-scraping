from dash import Dash, html
import pandas as pd

from src.components import round_dropdown, bar_chart

def create_layout(app: Dash, data: pd.DataFrame) -> html.Div:
    """Create the dashboard layout"""

    return html.Div(
        className="app-div",
        children=[
            html.H1(app.title),
            html.Hr(),
            html.Div(
                className="dropdown-container",
                children=[
                    round_dropdown.render(data)
                ]
            ),
            bar_chart.render(app, data)
        ]
    )