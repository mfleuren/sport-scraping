from unittest import result
import pandas as pd

def calculate_match_points(result_df: pd.DataFrame, points_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate points per match"""
    joined_df = result_df.join(points_df.set_index('RNK'), on='RNK', how='left')
    joined_df['POINTS'] = (joined_df['MATCH_LEVEL'] * joined_df['POINTS_RAW']).astype('int')
    joined_df.drop('POINTS_RAW', axis=1, inplace=True)
    return joined_df


if __name__ == '__main__':
    result_df = pd.read_csv('./temp/results_example.csv')
    points_df = pd.read_csv('./2022_Voorjaar/points.csv', sep=';')
    teams_df = pd.read_csv('./2022_Voorjaar/teams.csv', sep=';')
    
    match_points = calculate_match_points(result_df, points_df)

    print(match_points.head())