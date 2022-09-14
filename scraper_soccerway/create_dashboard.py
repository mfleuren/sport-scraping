from dash import Dash
from dash_bootstrap_components.themes import BOOTSTRAP
import pandas as pd


from dashboard.components.layout import create_layout

def main() -> None:

    data = pd.read_csv('.\\.\\results\\2022_Eredivisie\\points_coach.csv', sep=';')

    app = Dash(external_stylesheets=[BOOTSTRAP])
    app.title = 'WZV League Dashboard'
    app.layout = create_layout(app, data)
    app.run_server(debug=True)


if __name__ == '__main__':
    main()