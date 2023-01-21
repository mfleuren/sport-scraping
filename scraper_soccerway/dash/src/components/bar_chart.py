import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd

from . import ids

def render(app: Dash, data: pd.DataFrame) -> html.Div:

    @app.callback(
        Output(ids.BAR_CHART, "children"),
        [
            Input(ids.ROUND_DROPDOWN, "value")
        ]
    )
    def update_bar_chart(round: str) -> html.Div:
        filtered_data = data[data["Speelronde"] == round]
        pivotted_data = filtered_data.groupby("Coach", as_index=False)["P_Totaal"].sum().sort_values(by="P_Totaal", ascending=True)

        if filtered_data.shape[0] == 0:
            return html.Div("Geen data beschikbaar", id=ids.BAR_CHART)
        
        fig = px.bar(
            pivotted_data,
            x="P_Totaal",
            y="Coach",
            color="P_Totaal",
            barmode="group"
        )

        return html.Div(dcc.Graph(figure=fig), id=ids.BAR_CHART)
    return html.Div(id=ids.BAR_CHART)
