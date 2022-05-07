from typing import Tuple
import pandas as pd
import numpy as np
from scraper_pcs.process_results import list_best_coaches
from utility.result_objects import StageResults, Message

def calculate_match_points(results: StageResults, stage_race: bool = False) -> StageResults:
    """Calculate points per match by joining match results, points and coached teams"""

    result_df = results.stage_results[-1]

    if stage_race:
        points = results.default_points.set_index(['RANKING', 'RNK'])
        join_result_points = result_df.join(points, on=['RANKING', 'RNK'])
        join_result_points.fillna({'POINTS':0}, inplace=True) 

        grouped_points_by_rider = (
            join_result_points
                .groupby('RIDER', as_index=False)
                .agg({'MATCH':'first', 'POINTS':'sum'})
                .sort_values(by='POINTS', ascending=False)
                .reset_index(drop=True)
            )
                
        results.stage_points.append(grouped_points_by_rider)

    else:
        join_result_points = result_df.join(results.default_points.set_index('RNK'), on='RNK', how='left')
        join_result_points['POINTS'] = (join_result_points['MATCH_LEVEL'] * join_result_points['POINTS_RAW']).astype('int')
        joined_df = results.teams.join(join_result_points.set_index('RIDER'), on='RIDER', how='outer')
        
        joined_df.fillna(
            {
                'MATCH':result_df['MATCH'][0],
                'MATCH_LEVEL':result_df['MATCH_LEVEL'][0],
                'POINTS':0,
            }, inplace=True)

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


def mask_scores_inactive_riders(scores: pd.DataFrame) -> pd.DataFrame:
    """Replace the scores of inactive riders with 0."""

    mask_in = np.array(scores['MATCH'] < scores['ROUND_IN'])
    mask_out = np.array(scores['MATCH'] >= scores['ROUND_OUT'])
    scores.loc[mask_in | mask_out, 'POINTS'] = 0

    return scores


def calculate_stage_points(results: StageResults) -> StageResults:
    """Calculate the points by stage, combining rankings by rider before joining with coach teams."""

    stage_result = results.stage_results[-1].copy()
    stage_result = stage_result[~stage_result['RNK'].isin(['DNS', 'DNF', 'DSQ', 'OTL'])]
    stage_result['RNK'] = stage_result['RNK'].astype('int')
    stage_points_by_rider = (
        stage_result
        .join(
            results.default_points.set_index(['RANKING', 'RNK']), 
            on=['RANKING', 'RNK']
            )
        .groupby('RIDER')
        .agg({
            'POINTS':'sum',
            'MATCH':'first'
        })
        .sort_values('POINTS', ascending=False)
    )

    stage_points_by_team = results.teams.join(stage_points_by_rider, on='RIDER')
    stage_points_by_team.fillna({'POINTS':0, 'MATCH':stage_result['MATCH'][0]}, inplace=True)
    stage_points_by_team = mask_scores_inactive_riders(stage_points_by_team)

    results.stage_points.append(stage_points_by_team)

    return results


