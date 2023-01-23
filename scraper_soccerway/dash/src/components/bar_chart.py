import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd

from . import ids

def render(app: Dash, data: pd.DataFrame) -> html.Div:

    @app.callback(
        Output(ids.BAR_CHART, "children"),
        [
            Input(ids.ROUND_DROPDOWN, "value"),
            Input(ids.COACH_DROPDOWN, "value"),
        ]
    )
    def update_bar_chart(rounds: list[str], coaches: list[str]) -> html.Div:

        filtered_data = data[data["Speelronde"].isin(rounds)]
        if filtered_data.shape[0] == 0:
            return html.Div("Geen data beschikbaar", id=ids.BAR_CHART)

        pivotted_data = filtered_data.groupby("Coach", as_index=False)["P_Totaal"].sum()
        pivotted_data["Coach_Selected"] = pivotted_data["Coach"].isin(coaches).astype(str)
        pivotted_data = pivotted_data.sort_values(by="P_Totaal", ascending=False)
        pivotted_data.rename({"P_Totaal":"Total Points"}, axis=1, inplace=True)

        color_discrete_map = {"True": "blue", "False": "red"}
        category_orders = {
            "Coach": pivotted_data["Coach"].tolist(),
            "Coach_Selected": ["True", "False"]
        }

        fig = px.bar(
            pivotted_data,
            x="Total Points",
            y="Coach",
            color="Coach_Selected",
            color_discrete_map=color_discrete_map,
            category_orders=category_orders,
            template="ggplot2",
            text_auto='.2f',
            barmode="overlay"
        )
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

        return html.Div(dcc.Graph(figure=fig), id=ids.BAR_CHART)
    return html.Div(id=ids.BAR_CHART)
