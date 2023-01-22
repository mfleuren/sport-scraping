from dash import Dash
import dash_bootstrap_components as dbc

from src.components.layout import create_layout
from src.data.loader import load_point_by_coach_data


def main() -> None:

    data = load_point_by_coach_data("././results/2022_Eredivisie/points_coach.csv")
    print(data.columns)

    app = Dash(external_stylesheets=[dbc.themes.GRID])
    app.title = "WZV League 2022-2023"
    app.layout = create_layout(app, data)
    app.run()


if __name__ == "__main__":
    main()