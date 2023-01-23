from dash import Dash, dash_table, html
from dash.dependencies import Input, Output
import pandas as pd

from . import ids

def render(app: Dash, data: pd.DataFrame) -> html.Div:

    @app.callback(
        Output(ids.ALL_PLAYERS_TABLE, "children"),
        [
            Input(ids.POSITION_DROPDOWN, "value"),
            Input(ids.CLUB_DROPDOWN, "value"),
            Input(ids.ROUND_DROPDOWN, "value")
        ]            
    )
    def update_data_table(positions: list[str], clubs: list[str], rounds: list[str]) -> html.Div:
        
        filtered_data = data[
            data["Positie"].isin(positions) &\
            data["Team"].isin(clubs) &\
            data["Speelronde"].isin(rounds)
            ]
        if filtered_data.shape[0] == 0:
            return html.Div("Geen data beschikbaar", id=ids.ALL_PLAYERS_TABLE)

        pivotted_data = filtered_data.groupby(["Speler", "Positie", "Team"], as_index=False)["P_Totaal"].sum().sort_values(by="P_Totaal", ascending=False)
        pivotted_data["P_Totaal"] = pivotted_data["P_Totaal"].round(2)
        pivotted_data.rename({"Speler":"Player", "Positie":"Position", "P_Totaal":"Total Points"}, axis=1, inplace=True)

        table = dash_table.DataTable(
            pivotted_data.to_dict("records"),
            [{"name": i, "id": i} for i in pivotted_data.columns],
            page_size=15
        )
        return html.Div(table, id=ids.ALL_PLAYERS_TABLE)
    return html.Div(id=ids.ALL_PLAYERS_TABLE)