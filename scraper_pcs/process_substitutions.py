from typing import Tuple
from distutils.util import strtobool
from unittest import result

from utility.result_objects import StageResults, Message
from utility import imgur_robot
from scraper_pcs.webscraper import scrape_website

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import os
from dotenv import load_dotenv
load_dotenv()

def calculate_hundredpercentrule(results_data: StageResults) -> StageResults:
    """Find the active riders that everybody has in their team."""

    teams = results_data.teams
    active_rider_count = teams.loc[teams['POSITION'] == 'In', 'RIDER'].value_counts()
    number_of_coaches = teams['COACH'].nunique()
    riders_to_drop = list(active_rider_count[active_rider_count == number_of_coaches].index)

    results_data.teams['ROUND_OUT'] = results_data.teams['ROUND_OUT'].where(
        ~results_data.teams['RIDER'].isin(riders_to_drop), 
        results_data.stage_results[-1]['MATCH'][0])

    if any(riders_to_drop):
        print('---------------------------')
        print('100% RULE ACTIVATED!!')
        print('For the following riders:')
        print(riders_to_drop)
        print('---------------------------')
    
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


def make_substitutions(results_data: StageResults, message: Message) -> Tuple[StageResults, Message]:

    coaches = results_data.teams['COACH'].unique()
    stage = results_data.stage_results[-1]['MATCH'][0]

    total_n_substitutions = []

    for coach in coaches:
        n_substitutions = results_data.teams[
            (results_data.teams['COACH'] == coach) & \
            (results_data.teams['ROUND_OUT'] == stage)
            ].shape[0]

        total_n_substitutions.append(n_substitutions)

        for sub in range(n_substitutions):
            coach_team = results_data.teams[results_data.teams['COACH'] == coach]
            coach_team_out = coach_team[coach_team['ROUND_OUT'] == stage]
            coach_team_subs = coach_team[(coach_team['POSITION'] == 'Sub') & (coach_team['ROUND_OUT'].isna())] 

            row_out = coach_team_out.iloc[sub]
            rider_out = row_out['RIDER']
            position_out = row_out['POSITION']
            if position_out == 'In':
                results_data = set_rider_to_position_out(results_data, coach, rider_out) 

                if coach_team_subs.shape[0] > 0:
                    row_in = coach_team_subs.iloc[0]
                    rider_in = row_in['RIDER']
                    message.substitution_list.append(f'[tr][td]{coach}[/td][td]{rider_out}[/td][td]{rider_in}[/td][/tr]')
                else:
                    rider_in = None
                    message.substitution_list.append(f'[tr][td]{coach}[/td][td]{rider_out}[/td][td]-[/td][/tr]')

                sub_in_mask = (results_data.teams['COACH'] == coach) & (results_data.teams['RIDER'] == rider_in)
                results_data.teams.loc[sub_in_mask, 'POSITION'] = 'In'
                results_data.teams.loc[sub_in_mask, 'ROUND_IN'] = stage

                # print(f"Rider {rider_out} in active team; Subsitution: {rider_in}")

            elif position_out == 'Sub':

                results_data = set_rider_to_position_out(results_data, coach, rider_out) 

                message.substitution_list.append(f'[tr][td]{coach}[/td][td]{rider_out}[/td][td]-[/td][/tr]')

                # print(f"Rider {rider_out} in substitutes")
            else:
                # Don't perform any action - rider is already out (f.i. due to hundred percent rule).
                pass

    return results_data, message


def process_substitutions(results_data: StageResults, message: Message) -> Tuple[StageResults, Message]:
    """
    Process the substitutions: 
    (1) Set Position to <Out> for Riders that should go out this round.
    (2) Set Position to <In> for first rider on the bench (<Sub> status)
    """

    message.substitution_list.append(f"[b]Wissels etappe {results_data.stage_results[-1]['MATCH'][0]:.0f}[/b]")
    message.substitution_list.append('[table][th]Coach[/th][th]Renner IN[/th][th]Renner UIT[/th]')   

    results_data = determine_stage_dropouts(results_data)
    results_data, message = make_substitutions(results_data, message)

    n_coaches = len(results_data.teams['COACH'].unique())
    rider_count = results_data.teams.loc[results_data.teams['POSITION']=='In'].groupby('RIDER')['COACH'].count()

    if any(rider_count == n_coaches):
        while any(rider_count == n_coaches):

            results_data = calculate_hundredpercentrule(results_data)
            results_data, message = make_substitutions(results_data, message)

            # Recalculate rider_count
            rider_count = results_data.teams.loc[results_data.teams['POSITION']=='In'].groupby('RIDER')['COACH'].count()
        pass
    else:
        message.substitution_list.append('[tr][td]Geen wissels.[/td][td][/td][td][/td][/tr]')

    message.substitution_list.append('[/table]')

    return results_data, message


def create_teams_plot(results_data: StageResults, message: Message) -> Message:

    teams = results_data.teams
    coaches = sorted(teams['COACH'].unique(), key=str.casefold)

    selected_riders = teams[(teams['COACH'].isin(coaches)) &\
                            ((teams['POSITION'] == 'In') | (teams['POSITION'] == 'Sub'))][['RIDER', 'COACH']]

    heatmap_data = pd.crosstab(selected_riders['RIDER'], selected_riders['COACH'])
    heatmap_data = heatmap_data.reindex(sorted(heatmap_data.columns, key=str.casefold), axis=1)

    for rider in heatmap_data.index:
        for coach in heatmap_data.columns:
            if (teams[(teams['COACH'] == coach) & (teams['RIDER'] == rider) & (teams['POSITION'] == 'Sub')]).shape[0] > 0:
                heatmap_data.loc[rider, coach] = 0.5

    subpositions = heatmap_data==0.5
    for coach in heatmap_data.columns:
        subs = teams[(teams['COACH'] == coach) &\
                    (teams['POSITION'] == 'Sub')].reset_index(drop=True)
        
        for rider in subs['RIDER']:
            subpositions.loc[rider, coach] = subs[subs['RIDER']==rider].index.values[0] + 1        

    f, ax = plt.subplots(1, figsize=(8,16), facecolor='white') #plt.subplots(1, figsize=(12,14))
    sns.heatmap(heatmap_data, ax=ax, cmap="Greens", linewidths=.5, cbar=False)
    sns.heatmap(heatmap_data[heatmap_data==0.5], annot=subpositions, annot_kws={'size':8}, ax=ax, linewidths=.5,  
                cmap="Greens", vmin=0, vmax=1, cbar=False)
    ax.xaxis.tick_top() # x axis on top
    ax.xaxis.set_label_position('top')
    plt.xticks(rotation=90)

    # Image location information
    PATH_RESULTS = os.path.join(os.getcwd(), 'results', f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}")
    file_name = os.path.join(PATH_RESULTS, f"teams_plot.png")
    f.savefig(file_name, bbox_inches='tight', orientation='portrait')

    plt.close(f)

    if strtobool(os.getenv('IMGUR_UPLOAD')):
        img_url = imgur_robot.upload_to_imgur(file_name)
        message.img_urls.append(img_url)
    else:
        print(f"No image uploaded; IMGUR_UPLOAD set to {os.getenv('IMGUR_UPLOAD')}")

    return message
      
      
if __name__ == '__main__':

    

    results_data = StageResults()
    results_data = scrape_website(results_data, results_data.matches.iloc[0], stage_race=True)
    
    process_substitutions(results_data)
    # print(results_data.teams[results_data.teams['ROUND_OUT'].notna()])
