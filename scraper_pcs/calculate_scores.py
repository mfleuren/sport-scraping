from typing import Tuple
import pandas as pd
from scraper_pcs.process_results import list_best_coaches
from utility.result_objects import StageResults, Message

def calculate_match_points(results: StageResults) -> StageResults:
    """Calculate points per match by joining match results, points and coached teams"""

    result_df = results.stage_results[-1]
    join_result_points = result_df.join(results.default_points.set_index('RNK'), on='RNK', how='left')
    join_result_points['POINTS'] = (join_result_points['MATCH_LEVEL'] * join_result_points['POINTS_RAW']).astype('int')
    joined_df = results.teams.join(join_result_points.set_index('RIDER'), on='RIDER', how='outer')
    joined_df.drop(['ROUND', 'PICK', 'POINTS_RAW'], axis=1, inplace=True)

    results.stage_points.append(joined_df)
    return results

def calculate_match_standings(results: StageResults, message: Message) -> Tuple[StageResults, Message]:
    """Group match result by coach, return ordered dataframe with points by coach"""

    match_points = results.stage_points[-1]
    stage_result = pd.DataFrame(data=match_points.groupby('COACH')['POINTS'].sum().sort_values(ascending=False))
    stage_result['MATCH'] = match_points.loc[match_points['MATCH'].notna(), 'MATCH'].unique()[0]
    stage_result['MATCH_LEVEL'] = match_points.loc[match_points['MATCH_LEVEL'].notna(), 'MATCH_LEVEL'].unique()[0]

    results.stage_standings.append(stage_result)
    message.coach_mentions.append(list_best_coaches(stage_result))

    return results, message

