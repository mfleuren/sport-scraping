from dash import dash_table, html

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components import ids


def render(data: DashData, rounds: list[int], coaches: list[str]) -> html.Div:

    filtered_data = data.substitutions.query(
        f"Speelronde == {rounds} & Coach == {coaches}"
    )

    if filtered_data.shape[0] == 0:
        return html.Div("Geen data beschikbaar", id=ids.SUBSTITUTIONS_TABLE)

    table = dash_table.DataTable(
        filtered_data.to_dict("records"),
        [{"name": i, "id": i} for i in filtered_data.columns],
        page_size=15,
    )
    return html.Div(table, id=ids.SUBSTITUTIONS_TABLE)
