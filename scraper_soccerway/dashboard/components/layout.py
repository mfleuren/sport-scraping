from dash import Dash, html
import dash_bootstrap_components as dbc

from . import bar_chart_round, bar_chart_gc, round_dropdown, coaches_dropdown


def create_layout(app: Dash) -> html.Div:
    return html.Div(
        className ="app-div", 
        children = [
            html.H1(app.title),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            className="dropdown-container",
                            children=[
                                round_dropdown.render(app)
                            ])
                    ),
                    dbc.Col(
                        html.Div(
                            className="dropdown-container",
                            children=[
                                coaches_dropdown.render(app)
                            ])
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        bar_chart_round.render(app),
                    ),
                    dbc.Col(
                        bar_chart_gc.render(app),
                    )
                ]
            )
            
        ]
    )