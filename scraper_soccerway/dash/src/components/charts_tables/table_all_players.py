from dash import dash_table, html
from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components import ids


def render(
    data: DashData, rounds: list[int], clubs: list[str], positions: list[str]
) -> html.Div:

    filtered_data = data.points_by_player.query(
        f"Speelronde == {rounds} & Team == {clubs} & Positie == {positions}"
    )

    if filtered_data.shape[0] == 0:
        return html.Div("Geen data beschikbaar", id=ids.ALL_PLAYERS_TABLE)

    pivotted_data = (
        filtered_data.groupby(["Speler", "Positie", "Team"], as_index=False)["P_Totaal"]
        .sum()
        .sort_values(by="P_Totaal", ascending=False)
    )
    pivotted_data["P_Totaal"] = pivotted_data["P_Totaal"].round(2)
    pivotted_data.rename(
        {"Speler": "Player", "Positie": "Position", "P_Totaal": "Total Points"},
        axis=1,
        inplace=True,
    )

    table = dash_table.DataTable(
        pivotted_data.to_dict("records"),
        [{"name": i, "id": i} for i in pivotted_data.columns],
        page_size=15,
    )
    return html.Div(table, id=ids.ALL_PLAYERS_TABLE)
