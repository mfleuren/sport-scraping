import pandas as pd

def calculate_wins_by_coach(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the wins by coach for each week in the data"""

    weekwinners = (df
    .groupby(["Coach", "Speelronde"], as_index=False)["P_Totaal"]
    .sum()
    .set_index("Coach")
    .groupby("Speelronde")["P_Totaal"]
    .idxmax()
    .value_counts()
    )

    weekwinners_rank = (pd.DataFrame(data=df["Coach"].unique(), columns=["Coach"])
    .set_index("Coach")
    .join(weekwinners)
    .fillna(0)
    .reset_index()
    .sort_values(by=["P_Totaal", "Coach"], ascending=[False, True], key=lambda x: x.astype(str).str.lower())
    .rename({"P_Totaal":"Total Wins"}, axis=1)
    )

    return weekwinners_rank