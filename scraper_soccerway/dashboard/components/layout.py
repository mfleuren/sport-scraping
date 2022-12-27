from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

from . import bar_chart_round, bar_chart_gc, round_dropdown, coaches_dropdown, ids


def create_layout(app: Dash, data: pd.DataFrame) -> html.Div:

    @app.callback(
        Output(ids.TAB_CONTENTS, 'children'),
        [Input(ids.TAB_TABS, 'value')]
        )
    def update_tab_content(tab: str) -> list:

        bar_chart_rnd = bar_chart_round.render(app, data)
        bar_chart_gen = bar_chart_gc.render(app, data)

        if tab == ids.TAB_STANDINGS: 
            print('in tab standings')
            return [
                dbc.Col(bar_chart_rnd),
                dbc.Col(bar_chart_gen)
                ]
                
        elif tab == ids.TAB_TEAMS:
            print('in tab teams')
            return []
        elif tab == ids.TAB_STATS:
            print('in tab stats')
            return []
        else:
            return []

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
            dcc.Tabs(
                id=ids.TAB_TABS, 
                value=ids.TAB_STANDINGS, 
                children=[
                    dcc.Tab(label='Standings', value=ids.TAB_STANDINGS),
                    dcc.Tab(label='Teams', value=ids.TAB_TEAMS),
                    dcc.Tab(label='Stats', value=ids.TAB_STATS),
                    ]
                ),
            dbc.Row(id=ids.TAB_CONTENTS)
                        
        ]
    )