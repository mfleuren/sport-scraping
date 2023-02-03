from dash import Dash
import dash_bootstrap_components as dbc

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.components.layout import create_layout


def main() -> Dash:
    data = DashData()
    app = Dash(external_stylesheets=[dbc.themes.GRID])
    app.title = "WZV League 2022-2023"
    app.layout = create_layout(app, data)
    return app


if __name__ == "__main__":
    app = main()
    server = app.server
    app.run()
