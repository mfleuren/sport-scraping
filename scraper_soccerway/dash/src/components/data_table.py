from dash import Dash, dash_table, html
from dash.dependencies import Input, Output
import pandas as pd

from . import ids

def render(app: Dash, data: pd.DataFrame) -> html.Div:

    @app.callback(
        Output(ids.DATA_TABLE, "children"),
        [
            Input(ids.ROUND_DROPDOWN, "value"),
            Input(ids.COACH_DROPDOWN, "value")
        ]            
    )
    def update_data_table(rounds: list[str], coaches: list[str]) -> html.Div:
        
        filtered_data = data[data["Speelronde"].isin(rounds) & data["Coach"].isin(coaches)]
        if filtered_data.shape[0] == 0:
            return html.Div("Geen data beschikbaar", id=ids.DATA_TABLE)

        pivotted_data = filtered_data.groupby(["Speler", "Coach"], as_index=False)["P_Totaal"].sum().sort_values(by="P_Totaal", ascending=False)

        table = dash_table.DataTable(
            pivotted_data.to_dict("records"),
            [{"name": i, "id": i} for i in pivotted_data.columns],
            page_size=15
        )
        return html.Div(table, id=ids.DATA_TABLE)
    return html.Div(id=ids.DATA_TABLE)