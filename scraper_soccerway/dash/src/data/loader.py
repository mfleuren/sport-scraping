import pandas as pd

def load_point_by_coach_data(path: str) -> pd.DataFrame:
    """Load data from a csv file"""

    data = pd.read_csv(path, sep=';')

    data["P_Totaal"] = data["P_Totaal"].round(2)

    return data