import plotly.express as px
from dash import dcc, html

from scraper_soccerway.dash.src.data.loader import DashData
from scraper_soccerway.dash.src.data.transformer import calculate_wins_by_coach


def render(data: DashData, rounds: list[int], coaches: list[str]) -> html.Div:

    filtered_data = data.points_by_coach.query(f"Speelronde <= {max(rounds)}")
    
    if filtered_data.shape[0] == 0:
        return html.Div("Geen data beschikbaar")

    pivotted_data = calculate_wins_by_coach(filtered_data)
    pivotted_data["Coach_Selected"] = pivotted_data["Coach"].isin(coaches).astype(str)

    color_discrete_map = {"True": "blue", "False": "red"}
    category_orders = {
        "Coach": pivotted_data["Coach"].tolist(),
        "Coach_Selected": ["True", "False"],
    }

    fig = px.bar(
        pivotted_data,
        x="Total Wins",
        y="Coach",
        color="Coach_Selected",
        color_discrete_map=color_discrete_map,
        category_orders=category_orders,
        template="ggplot2",
        text_auto=".2f",
        barmode="overlay",
    )
    fig.update_xaxes(
        range=[
            pivotted_data["Total Wins"].min(),
            pivotted_data["Total Wins"].max() + 1,
        ],
        dtick=1
    )
    fig.update_traces(
        textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, texttemplate='%{x:.0}'
    )
    return html.Div(children=dcc.Graph(figure=fig))
