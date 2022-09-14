from dash import Dash, html
import dash_bootstrap_components as dbc
import pandas as pd

from . import bar_chart_round, bar_chart_gc, round_dropdown, coaches_dropdown


def create_layout(app: Dash, data: pd.DataFrame) -> html.Div:
    return html.Div(
        className ="app-div", 
        children = [
            html.H1(app.title),
            html.Hr(),
            dbc.Row(
                children=[
                    dbc.Col(
                        className="dropdown-container",
                        children=[round_dropdown.render(app, data)]
                    ),
                    dbc.Col(
                        className="dropdown-container",
                        children=[coaches_dropdown.render(app, data)]
                    )
                ]
            ),
            dbc.Row(
                children=[
                    dbc.Col(bar_chart_round.render(app, data)),
                    dbc.Col(bar_chart_gc.render(app, data))
                ]
            )
            
        ]
    )