import pandas as pd

def calculate_match_points(result_df: pd.DataFrame, points_df: pd.DataFrame, teams_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate points per match by joining match results, points and coached teams"""

    join_result_points = result_df.join(points_df.set_index('RNK'), on='RNK', how='left')
    join_result_points['POINTS'] = (join_result_points['MATCH_LEVEL'] * join_result_points['POINTS_RAW']).astype('int')
    joined_df = join_result_points.join(teams_df.set_index('RIDER'), on='RIDER', how='left')
    joined_df.drop(['ROUND', 'PICK', 'POINTS_RAW'], axis=1, inplace=True)
    return joined_df

def calculate_stage_result(match_points: pd.DataFrame) -> pd.DataFrame:
    """Group match result by coach, return ordered dataframe with points by coach"""

    stage_result = pd.DataFrame(data=match_points.groupby('COACH')['POINTS'].sum().sort_values(ascending=False))
    stage_result['MATCH'] = match_points.loc[0, 'MATCH']
    stage_result['MATCH_LEVEL'] = match_points.loc[0, 'MATCH_LEVEL']

    return stage_result


if __name__ == '__main__':
    result_df = pd.read_csv('./temp/results_example.csv')
    points_df = pd.read_csv('./2022_Voorjaar/points.csv', sep=';')
    teams_df = pd.read_csv('./2022_Voorjaar/teams.csv', sep=';')
    
    match_points = calculate_match_points(result_df, points_df, teams_df)
    stage_result = calculate_stage_result(match_points)
    print(stage_result.head())

