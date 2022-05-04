import os
import sys
from unittest import result
sys.path.insert(1, os.getcwd())
from utility.result_objects import StageResults, Message
from scraper_pcs.webscraper import scrape_website

def calculate_hundredpercentrule(results_data: StageResults) -> StageResults:
    """Find the active riders that everybody has in their team."""

    teams = results_data.teams
    active_rider_count = teams.loc[teams['POSITION'] == 'In', 'RIDER'].value_counts()
    number_of_coaches = teams['COACH'].nunique()
    riders_to_drop = list(active_rider_count[active_rider_count == number_of_coaches].index)

    results_data.teams['ROUND_OUT'] = results_data.teams['ROUND_OUT'].where(
        ~results_data.teams['RIDER'].isin(riders_to_drop), 
        results_data.stage_results[-1]['MATCH'][0])
    
    return results_data


def determine_stage_dropouts(results_data: StageResults) -> StageResults:
    """
    Determine which riders did not finish the most recent stage.
    ------
    Rules:
    ------ 
    DNS (Did not start): substitute this stage
    DNF (Did not finish): substitute next stage
    OTL (Out of time limit): substitute next stage
    DSQ (Disqualified): substitute next stage
    """

    stage_results = results_data.stage_results[-1]
    current_stage = stage_results['MATCH'][0]

    riders_to_drop_this_stage = stage_results.loc[stage_results['RNK'] == 'DNS', ['RIDER', 'MATCH']]
    riders_to_drop_next_stage = stage_results.loc[stage_results['RNK'].isin(['DNF', 'OTL', 'DSQ']), ['RIDER', 'MATCH']]

    results_data.teams['ROUND_OUT'] = results_data.teams['ROUND_OUT'].where(
        ~results_data.teams['RIDER'].isin(riders_to_drop_this_stage['RIDER']), 
        current_stage)
    results_data.teams['ROUND_OUT'] = results_data.teams['ROUND_OUT'].where(
        ~results_data.teams['RIDER'].isin(riders_to_drop_next_stage['RIDER']), 
        current_stage+1)

    return results_data


def set_rider_to_position_out(results_data: StageResults, coach: str, rider_out: str) -> StageResults:

    sub_out_mask = (results_data.teams['COACH'] == coach) & (results_data.teams['RIDER'] == rider_out)
    results_data.teams.loc[sub_out_mask, 'POSITION'] = 'Out'

    return results_data


def make_substitutions(results_data: StageResults) -> StageResults:


    coaches = results_data.teams['COACH'].unique()
    stage = results_data.stage_results[-1]['MATCH'][0]

    for coach in coaches:
        n_substitutions = results_data.teams[
            (results_data.teams['COACH'] == coach) & \
            (results_data.teams['ROUND_OUT'] == stage)
            ].shape[0]

        for sub in range(n_substitutions):
            coach_team = results_data.teams[results_data.teams['COACH'] == coach]
            coach_team_out = coach_team[coach_team['ROUND_OUT'] == stage]
            coach_team_subs = coach_team[(coach_team['POSITION'] == 'Sub') & (coach_team['ROUND_OUT'].isna())] 

            row_out = coach_team_out.iloc[sub]
            rider_out = row_out['RIDER']
            position_out = row_out['POSITION']
            if position_out == 'In':
                results_data = set_rider_to_position_out(results_data, coach, rider_out) 

                if coach_team_subs is not None:
                    row_in = coach_team_subs.iloc[0]
                    rider_in = row_in['RIDER']

                    sub_in_mask = (results_data.teams['COACH'] == coach) & (results_data.teams['RIDER'] == rider_in)
                    results_data.teams.loc[sub_in_mask, 'POSITION'] = 'In'
                    results_data.teams.loc[sub_in_mask, 'ROUND_IN'] = stage

                print(f"Rider {rider_out} in active team; Subsitution: {rider_in}")

            elif position_out == 'Sub':

                results_data = set_rider_to_position_out(results_data, coach, rider_out) 

                print(f"Rider {rider_out} in substitutes")
            else:
                # Don't perform any action - rider is already out (f.i. due to hundred percent rule).
                pass

    return results_data


def process_substitutions(results_data: StageResults) -> StageResults:
    """
    Process the substitutions: 
    (1) Set Position to <Out> for Riders that should go out this round.
    (2) Set Position to <In> for first rider on the bench (<Sub> status)
    """

    n_coaches = len(results_data.teams['COACH'].unique())
    rider_count = results_data.teams.loc[results_data.teams['POSITION']=='In'].groupby('RIDER')['COACH'].count()

    results_data = determine_stage_dropouts(results_data)

    while any(rider_count == n_coaches):

        results_data = calculate_hundredpercentrule(results_data)
        results_data = make_substitutions(results_data)

        # Recalculate rider_count
        rider_count = results_data.teams.loc[results_data.teams['POSITION']=='In'].groupby('RIDER')['COACH'].count()
            
    return results_data
      
      
if __name__ == '__main__':

    

    results_data = StageResults()
    results_data = scrape_website(results_data, results_data.matches.iloc[0], stage_race=True)
    
    process_substitutions(results_data)
    # print(results_data.teams[results_data.teams['ROUND_OUT'].notna()])
