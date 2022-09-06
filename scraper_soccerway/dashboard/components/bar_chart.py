import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd

from . import ids


data = pd.read_csv('.\\.\\results\\2022_Eredivisie\\points_coach.csv', sep=';')

def render(app: Dash) -> html.Div:
    
    @app.callback(
        Output(ids.BAR_CHART, "children"),
        [
            Input(ids.ROUND_DROPDOWN, "value")
        ]
    )
    def update_bar_chart(speelrondes: list[int]) -> html.Div:
        filtered_data = data[data['Speelronde'].isin(speelrondes)]

        if filtered_data.shape[0] == 0:
            return html.Div("No data selected.", id=ids.BAR_CHART)
        
        grouped_data = filtered_data.groupby('Coach', as_index=False)['P_Totaal'].sum()

        fig = px.bar(grouped_data, x='P_Totaal', y='Coach', text='Coach')

        return html.Div(dcc.Graph(figure=fig), id=ids.BAR_CHART)
    return html.Div(id=ids.BAR_CHART)
