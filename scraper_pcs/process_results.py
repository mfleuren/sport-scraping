import pandas as pd
import numpy as np
import os, sys 
from distutils.util import strtobool
import itertools

sys.path.append(os.getcwd())

from utility.result_objects import StageResults, Message
from utility import imgur_robot

import matplotlib.pyplot as plt
import seaborn as sns


# Image location information
PATH_RESULTS = os.path.join(os.getcwd(), 'results', f"{os.getenv('COMPETITION_YEAR')}_{os.getenv('COMPETITION_NAME')}")

# Image formatting
JITTER_THRESHOLD = 0.1
FONTSIZE = 8
DPI=200


def calculate_stage_winners(df: pd.DataFrame) -> pd.Series:
    """Calculate the number of stage wins by coach."""

    stage_results = df[df['POSITION']=='In'].groupby(['MATCH', 'COACH'])['POINTS'].sum()
    stage_results_rank = stage_results.groupby('MATCH').rank(method='min', ascending=False).reset_index()
    wins_by_coach = stage_results_rank[(stage_results_rank['POINTS'] == 1)].groupby('COACH')['MATCH'].count()
    print(wins_by_coach)

    return wins_by_coach


def create_swarm_plot(
    results: StageResults,
    message_data: Message,
    gc_check: bool = False
    ):

    if not gc_check:
        data = results.stage_points[-1]
        match_name = data.loc[data['MATCH'].notna(), 'MATCH'].unique()[0]
        match_name = f'Stage_{int(match_name)}' if type(match_name) != 'str' else match_name
        file_name = os.path.join(PATH_RESULTS, f"{match_name.lower()}_plot.png")
    else: 
        data = results.all_points
        match_name = 'Algemeen Klassement'
        file_name = os.path.join(PATH_RESULTS, f"{match_name.lower()}_plot.png")

    if 'POSITION' in data.columns:
        data = data[data['POSITION'] == 'In']

    gc = pd.DataFrame(data.groupby('COACH')['POINTS'].sum().sort_values(ascending=False))
    gc.reset_index(inplace=True)
    gc['RELATIVE_POSITION'] = (gc['POINTS'] - gc['POINTS'].min())/(gc['POINTS'].max() - gc['POINTS'].min())
    gc['YPOSITION_TEXT'] = gc['POINTS'].max() - (-gc['POINTS']).argsort()*((gc['POINTS'].max() - gc['POINTS'].min())/(gc['COACH'].nunique()-1))

    print(gc[["COACH", "POINTS"]].head())
    coach_hue_order = gc.loc[gc['COACH'].str.lower().argsort(), 'COACH'].values
    mks = itertools.cycle(['o', '^', 'p', 's', 'D', 'P'])
    markers = [next(mks) for _ in gc["COACH"].unique()]
    palette = sns.color_palette('colorblind', n_colors=gc.shape[0])

    def jitter(shape, magnitude):
        return 1+np.random.uniform(magnitude, -magnitude, shape)

    f = plt.figure(figsize=(1028/DPI,720/DPI), dpi=DPI, edgecolor=None)

    # Grid and grid labels
    steps_to_choose_from = [200, 150, 100, 75, 50, 40, 30, 25, 20, 10, 8, 6, 4, 2]
    diffpart = (gc['POINTS'].max() - gc['POINTS'].min()) / 4
    diffrel = [(diffpart / val) for val in steps_to_choose_from]
    chosen_step = steps_to_choose_from[next(x[0] for x in enumerate(diffrel) if x[1] > 1)]
    ygrid = np.arange(gc['POINTS'].max(), gc['POINTS'].min(), step=-chosen_step)
    plt.hlines(y=ygrid[0], xmin=0.9, xmax=1.1, colors='k', linestyles='dashed', linewidth=0.5)
    plt.hlines(y=ygrid[1:], xmin=0.9, xmax=1.1, colors='k', linestyles=(0, (1, 10)), linewidth=0.5)
    for y in ygrid[1:]:
        diff = y - gc['POINTS'].max()
        plt.text(
            x=1.1, y=y*.9925, s=f'{diff:.0f}',
            horizontalalignment='right', verticalalignment='top', size=5.0
            )

    # Stage winners
    if gc_check:
        stage_winners = calculate_stage_winners(data)
        gc = gc.join(stage_winners, on='COACH').rename({'MATCH':'WINS'}, axis=1)
        gc['WINS'].fillna(0, inplace=True)
        gc['WINS'] = gc['WINS'].astype('int')
    else:
        gc['WINS'] = 0

    # Coach labels
    for _, row in gc.iterrows():
        text_label = f"{'+' * row['WINS']} {row['COACH']} ({row['POINTS']:.0f} p.)"
        idx = np.argmax(row['COACH'] == coach_hue_order)
        plt.text(
            x=0.81, 
            y=row['YPOSITION_TEXT'], 
            s=text_label, 
            color=palette[idx], 
            fontdict={
                'size':FONTSIZE, 
                'verticalalignment':'center', 
                'horizontalalignment':'right'
                }
                )
        plt.scatter(
            0.825,
            row['YPOSITION_TEXT'],
            marker=markers[idx],
            color=palette[idx],
            s=20
        )

    # Actual scatterplot
    sns.scatterplot(
        x=jitter(gc['POINTS'].shape, 0.033),
        y=gc['POINTS'],
        hue=gc['COACH'],
        hue_order=coach_hue_order,
        style=gc['COACH'],
        markers=markers,
        style_order=coach_hue_order,
        palette=palette
    )

    plt.xlim(left=0.6, right=1.15)
    plt.title(match_name.replace('_', ' '), fontdict={'size':1.25*FONTSIZE, 'weight':'bold'})

    ax = plt.gca()
    ax.get_legend().remove()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.spines[['top', 'bottom', 'left', 'right']].set_visible(False)
    f.savefig(file_name, bbox_inches='tight', orientation='portrait')
    # plt.show()
    plt.close(f)

    if strtobool(os.getenv('IMGUR_UPLOAD')):
        img_url = imgur_robot.upload_to_imgur(file_name)
        message_data.img_urls.append(img_url)
    else:
        print(f"No image uploaded; IMGUR_UPLOAD set to {os.getenv('IMGUR_UPLOAD')}")

    return message_data


def create_echelon_plot(
    results: StageResults, 
    message_data: Message,
    gc_check: bool = False
    ) -> Message:

    if not gc_check:
        data = results.stage_points[-1]
        match_name = data.loc[data['MATCH'].notna(), 'MATCH'].unique()[0]
        match_name = f'Stage_{int(match_name)}' if type(match_name) != 'str' else match_name
        file_name = os.path.join(PATH_RESULTS, f"{match_name.lower()}_plot.png")
    else: 
        data = results.all_points
        match_name = 'Algemeen Klassement'
        file_name = os.path.join(PATH_RESULTS, f"{match_name.lower()}_plot.png")

    if 'POSITION' in data.columns:
        data = data[data['POSITION'] == 'In']

    gc = pd.DataFrame(data.groupby('COACH')['POINTS'].sum().sort_values(ascending=False))
    gc.reset_index(inplace=True)
    gc['RELATIVE_POSITION'] = (gc['POINTS'] - gc['POINTS'].min())/(gc['POINTS'].max() - gc['POINTS'].min())
    gc['ECHELON'] = (gc['RELATIVE_POSITION'].shift(1) > (gc['RELATIVE_POSITION'] + JITTER_THRESHOLD)).cumsum()
    gc['ECHELON_POSITION'] = gc.groupby('ECHELON').cumcount()
    gc['ECHELON_MAXPOINTS'] = gc['ECHELON'].map(gc.groupby('ECHELON')['POINTS'].max())
    gc['XJITTER'] = 1 + gc['ECHELON_POSITION'] * 0.07
    gc['YJITTER'] = gc['POINTS'].max() - (-gc['POINTS']).argsort()*((gc['POINTS'].max() - gc['POINTS'].min())/(gc['COACH'].nunique()-1))

    coach_hue_order = gc.loc[gc['COACH'].str.lower().argsort(), 'COACH'].values

    f = plt.figure(figsize=(1028/DPI,720/DPI), dpi=DPI, edgecolor=None)

    ygrid = np.linspace(
        start=gc['POINTS'].max(), 
        stop=np.round(gc['POINTS'].min(), -2),
        num=4)

    plt.hlines(y=ygrid[0], xmin=0.95, xmax=gc['XJITTER'].max()*1.05, colors='k', linestyles='dashed', linewidth=0.5)
    plt.hlines(y=ygrid[1:], xmin=0.95, xmax=gc['XJITTER'].max()*1.05, colors='k', linestyles=(0, (1, 10)), linewidth=0.5)

    for y in ygrid[1:]:
        diff = y - gc['POINTS'].max()
        plt.text(
            x=gc['XJITTER'].max()*1.05, y=y*.9925, s=f'{diff:.0f}',
            horizontalalignment='right', verticalalignment='top', size=5.0
            )

    palette = sns.color_palette('colorblind', n_colors=gc.shape[0])
    sns.scatterplot(
        data=gc, 
        x='XJITTER', 
        y='POINTS', 
        hue='COACH', 
        hue_order=coach_hue_order, 
        palette='colorblind',
        ax=plt.gca())

    for _, row in gc.iterrows():

        text_label = f"{row['COACH']} ({row['POINTS']:.0f} p.)"
        palette_idx = np.argmax(row['COACH'] == coach_hue_order)
        plt.text(
            x=0.9, 
            y=row['YJITTER'], 
            s=text_label, 
            color=palette[palette_idx], 
            fontdict={
                'size':FONTSIZE, 
                'verticalalignment':'center', 
                'horizontalalignment':'right'
                }
                )
        plt.plot(
            [0.925, row['XJITTER']],
            [row['YJITTER'], row['POINTS']],
            color=palette[palette_idx],
            linewidth=0.25
        )

    plt.xlim(left=0.75, right=2)
    plt.title(match_name.replace('_', ' '), fontdict={'size':1.25*FONTSIZE, 'weight':'bold'})

    ax = plt.gca()
    ax.get_legend().remove()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.spines[['top', 'bottom', 'left', 'right']].set_visible(False)
    f.savefig(file_name, bbox_inches='tight', orientation='portrait')
    # plt.show()
    plt.close(f)

    if strtobool(os.getenv('IMGUR_UPLOAD')):
        img_url = imgur_robot.upload_to_imgur(file_name)
        message_data.img_urls.append(img_url)
    else:
        print(f"No image uploaded; IMGUR_UPLOAD set to {os.getenv('IMGUR_UPLOAD')}")

    return message_data


def create_teams_message(data: pd.DataFrame) -> str:

    data['POINTS_STR'] = data['POINTS'].fillna(0).astype(int).astype(str)
    if 'ROUND_OUT' in data.columns:
        data.loc[data['ROUND_OUT'] <= data['MATCH'], 'POINTS_STR'] = 'X'
        data.loc[(data['ROUND_IN'] > data['MATCH']) | data['ROUND_IN'].isna(), 'POINTS_STR'] = 'S'
    dfg1 = data.groupby(['COACH', 'RIDER'], as_index=False)['POINTS_STR'].apply(lambda x: '-'.join(x))
    dfg2 = data[data['POSITION']=='In'].groupby(['COACH', 'RIDER'])['POINTS'].sum()
    dfg = dfg1.join(dfg2, on=['COACH', 'RIDER'])
    dfg['POINTS'] = dfg['POINTS'].fillna(0)

    message = []
    message.append('[b]Overzicht teams en punten per renner:[/b][spoiler]')

    for coach in sorted(dfg['COACH'].unique(), key=str.casefold):

        message.append('[b]' + coach + '[/b][spoiler][table]')
        for row in dfg[dfg['COACH'] == coach].iterrows():
            message.append(f"[tr][td]{row[1]['RIDER']}[/td][td]{row[1]['POINTS']:.0f}:\t({row[1]['POINTS_STR']})[/td][/tr]")
        message.append('[/spoiler][/table]')

    message.append('[/spoiler]')
    message = ''.join(message)

    return message


def list_best_coaches(data: pd.DataFrame) -> list:

    ranked_data = data.groupby('COACH')['POINTS'].sum().sort_values(ascending=False)
    best_coaches = ranked_data.head(3).index.to_list()
    print(f'Best coaches: {best_coaches}')

    return best_coaches


def create_mention_string(coaches: list) -> str:

    unique_coaches = np.unique(coaches)

    mention_list = ['Mentions voor de beste coaches in de etappe en het algemeen klassement: ']
    for coach in unique_coaches:
        mention_list.append(f'@{coach} ')
    mention_string = ''.join(mention_list) + f'\n'

    return mention_string


def create_image_string(img_urls: list) -> str:
    return ''.join(img_urls)


def create_subs_message(subs_list: list) -> str:
    return ''.join(subs_list)


def create_forum_message(results_data: StageResults, message_data: Message) -> str:

    substitution_message = create_subs_message(message_data.substitution_list)
    teams_message = create_teams_message(results_data.all_points)
    image_message = create_image_string(message_data.img_urls)
    mentions_message = create_mention_string(message_data.coach_mentions)

    return substitution_message + image_message + mentions_message + teams_message


def summary_plot_by_draft_round(results_data: StageResults, message_data: Message) -> Message:

    df_teams = results_data.teams
    df_results = results_data.all_points

    # Set round as categorical
    df_teams['ROUND'] = df_teams['ROUND'].astype('category')

    # Get total points by rider and SURNAME into Teams DF
    df_teams = df_teams.join(df_results
                         .groupby('RIDER')
                         .agg({'POINTS':'sum', 'SURNAME':'first'})
                         , on='RIDER')

    # Calculate outliers
    df_teams = (df_teams.join(
        df_teams.groupby('ROUND')['POINTS']
        .agg([lambda x: x.quantile(0.75) + 1.5*(x.quantile(0.75) - x.quantile(0.25))])
        .rename({'<lambda>':'OUTLIER_EDGE'}, axis=1)
        , on='ROUND'
        ))
    df_teams['OUTLIER'] = df_teams['POINTS'] > df_teams['OUTLIER_EDGE']

    # Create plot
    f = plt.figure(figsize=(720/DPI,512/DPI), dpi=DPI)
    ax = plt.gca()
    ax.spines[['right', 'top']].set_visible(False)
    sns.boxplot(data=df_teams, x='ROUND', y='POINTS', ax=ax, fliersize=0, 
                boxprops={'alpha':0.5}, 
                whiskerprops={'alpha':0.5},
                capprops={'alpha':0.5},
                medianprops={'alpha':0.5}
            )
    sns.swarmplot(
        data=df_teams, x='ROUND', y='POINTS', ax=ax, marker='d', size=10)

    # Plot outlier names
    for _, row in df_teams[df_teams['OUTLIER']].iterrows():
        plt.text(row['ROUND']-0.9, row['POINTS'], row['SURNAME'], ha='left', va='bottom', rotation=30)

    # Save figure and upload
    file_name = os.path.join(PATH_RESULTS, f"summary_draft_{os.getenv('COMPETITION_NAME').lower() + os.getenv('COMPETITION_YEAR')}_plot.png")
    f.savefig(file_name, bbox_inches='tight', orientation='landscape')

    if strtobool(os.getenv('IMGUR_UPLOAD')):
        img_url = imgur_robot.upload_to_imgur(file_name)
        message_data.img_urls.append(img_url)
    else:
        print(f"No image uploaded; IMGUR_UPLOAD set to {os.getenv('IMGUR_UPLOAD')}")
        
    return message_data
    
    
if __name__ == '__main__':

    import utility.result_objects as result_objects
    results_data = result_objects.StageResults()
    message_data = result_objects.Message()
    create_swarm_plot(results_data, message_data, gc_check=True)