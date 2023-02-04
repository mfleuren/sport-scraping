from dash import Dash, dash_table, html
from dash.dependencies import Input, Output

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components import ids


def render(app: Dash, data: DashData) -> html.Div:
    @app.callback(
        Output(ids.CHOSEN_PLAYERS_TABLE, "children"),
        [Input(ids.ROUND_DROPDOWN, "value"), Input(ids.COACH_DROPDOWN, "value")],
    )
    def update_data_table(rounds: list[int], coaches: list[str]) -> html.Div:

        filtered_data = data.points_by_coach[
            data.points_by_coach["Speelronde"].isin(rounds)
            & data.points_by_coach["Coach"].isin(coaches)
        ]
        if filtered_data.shape[0] == 0:
            return html.Div("Geen data beschikbaar", id=ids.CHOSEN_PLAYERS_TABLE)

        pivotted_data = (
            filtered_data.groupby(["Speler", "Coach"], as_index=False)["P_Totaal"]
            .sum()
            .sort_values(by="P_Totaal", ascending=False)
        )
        pivotted_data["P_Totaal"] = pivotted_data["P_Totaal"].round(2)
        pivotted_data.rename(
            {"Speler": "Player", "P_Totaal": "Total Points"}, axis=1, inplace=True
        )

        table = dash_table.DataTable(
            pivotted_data.to_dict("records"),
            [{"name": i, "id": i} for i in pivotted_data.columns],
            page_size=15,
        )
        return html.Div(table, id=ids.CHOSEN_PLAYERS_TABLE)

    return html.Div(id=ids.CHOSEN_PLAYERS_TABLE)
