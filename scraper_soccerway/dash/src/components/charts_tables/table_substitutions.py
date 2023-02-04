from dash import Dash, dash_table, html
from dash.dependencies import Input, Output

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components import ids

def render(app: Dash, data: DashData) -> html.Div:

    @app.callback(
        Output(ids.SUBSTITUTIONS_TABLE, "children"),
        [Input(ids.ROUND_DROPDOWN, "value"), Input(ids.COACH_DROPDOWN, "value")],
    )
    def update_data_table(rounds: list[int], coaches: list[str]) -> html.Div:
        
        filtered_data = data.substitutions[
            data.substitutions["Coach"].isin(coaches) &\
            data.substitutions["Speelronde"].isin(rounds)
            ]
        if filtered_data.shape[0] == 0:
            return html.Div("Geen data beschikbaar", id=ids.SUBSTITUTIONS_TABLE)

        table = dash_table.DataTable(
            filtered_data.to_dict("records"),
            [{"name": i, "id": i} for i in filtered_data.columns],
            page_size=15
        )
        return html.Div(table, id=ids.SUBSTITUTIONS_TABLE)
    return html.Div(id=ids.SUBSTITUTIONS_TABLE)