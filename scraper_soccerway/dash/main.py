from dash import Dash
import dash_bootstrap_components as dbc

from scraper_soccerway.dash.src.components.layout import create_layout
from scraper_soccerway.dash.src.data.loader import load_points_by_coach_data, load_points_by_player_data


teams_data = load_points_by_coach_data("scraper_soccerway/dash/data/")
players_data = load_points_by_player_data("scraper_soccerway/dash/data/")

app = Dash(external_stylesheets=[dbc.themes.GRID])
app.title = "WZV League 2022-2023"
app.layout = create_layout(app, teams_data, players_data)
app.run()