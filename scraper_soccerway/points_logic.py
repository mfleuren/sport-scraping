import pandas as pd

from data_processing import CompetitionData


def calculate_point_by_player(data: CompetitionData) -> pd.DataFrame:
    """Perform points calculations"""

    events = data.match_events.copy()
    player = data.dim_players.copy()

    events_player = events.join(
        player[["Link", "Positie"]].set_index("Link"), on="Link"
    )
    points_scheme = data.points_scheme.copy().set_index("Positie")
    points_player = events_player.join(
        points_scheme, on="Positie", lsuffix="_e", rsuffix="_p"
    )

    points_player[
        [
            "Wedstrijd_Gewonnen_e",
            "Wedstrijd_Gelijk_e",
            "Wedstrijd_Verloren_e",
            "CleanSheet_e",
        ]
    ] = points_player[
        [
            "Wedstrijd_Gewonnen_e",
            "Wedstrijd_Gelijk_e",
            "Wedstrijd_Verloren_e",
            "CleanSheet_e",
        ]
    ].astype(
        "bool"
    )

    points_player["P_Gespeeld"] = points_player["Wedstrijd_Gespeeld"] * (
        points_player["Minuten_Gespeeld"] / points_player["Match_Duration"]
    )
    points_player["P_Gewonnen"] = (
        points_player["Wedstrijd_Gewonnen_p"]
        * points_player["Wedstrijd_Gewonnen_e"]
        * (points_player["Minuten_Gespeeld"] / points_player["Match_Duration"])
    )
    points_player["P_Gelijk"] = (
        points_player["Wedstrijd_Gelijk_p"]
        * points_player["Wedstrijd_Gelijk_e"]
        * (points_player["Minuten_Gespeeld"] / points_player["Match_Duration"])
    )
    points_player["P_Verloren"] = (
        points_player["Wedstrijd_Verloren_p"]
        * points_player["Wedstrijd_Verloren_e"]
        * (points_player["Minuten_Gespeeld"] / points_player["Match_Duration"])
    )
    points_player["P_Kaart_Geel"] = (
        points_player["Kaart_Geel_p"] * points_player["Kaart_Geel_e"]
    )
    points_player["P_Kaart_Rood"] = (
        points_player["Kaart_Rood_p"] * points_player["Kaart_Rood_e"]
    )
    points_player["P_Doelpunt"] = points_player["Doelpunt"] * points_player["Goal"]
    points_player["P_Assist"] = points_player["Assist_p"] * points_player["Assist_e"]
    points_player["P_Tegendoelpunt"] = (
        points_player["Tegendoelpunt_p"]
        * points_player["Tegendoelpunt_e"]
        * (points_player["Minuten_Gespeeld"] > 0).astype("int")
    )
    points_player["P_Eigen_Doelpunt"] = (
        points_player["Eigen_Doelpunt"] * points_player["Goal_Eigen"]
    )
    points_player["P_Clean_Sheet"] = (
        points_player["CleanSheet_p"]
        * points_player["CleanSheet_e"]
        * (points_player["Minuten_Gespeeld"] / points_player["Match_Duration"])
    )
    points_player["P_Penalty_Gescoord"] = (
        points_player["Penalty_Gescoord"] * points_player["Penalty_Goal"]
    )
    points_player["P_Penalty_Gemist"] = (
        points_player["Penalty_Gemist_p"] * points_player["Penalty_Gemist_e"]
    )
    points_player["P_Penalty_Gestopt"] = (
        points_player["Penalty_Gestopt_p"] * points_player["Penalty_Gestopt_e"]
    )

    cols_to_keep = ["Speler", "Link", "Datum"] + points_player.columns[
        points_player.columns.str.contains("P_")
    ].tolist()
    cols_to_drop = points_player.columns[~points_player.columns.isin(cols_to_keep)]
    points_player.drop(cols_to_drop, axis=1, inplace=True)
    points_player["P_Totaal"] = points_player.drop(
        ["Speler", "Link", "Datum"], axis=1
    ).sum(axis=1)

    data.points_player = points_player.round(2)

    return data


def calculate_points_by_coach(data: CompetitionData) -> CompetitionData:
    """Calculate points by team selections"""

    cols_to_drop = data.points_player.columns[
        ~data.points_player.columns.isin(["Link", "P_Totaal"])
    ]
    data.points_coach = data.chosen_teams.join(
        data.points_player.drop(cols_to_drop, axis=1).set_index("Link"), on="Link"
    )

    return data
