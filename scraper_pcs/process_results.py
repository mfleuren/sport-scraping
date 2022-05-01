import pandas as pd
import numpy as np
import os 
from distutils.util import strtobool

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

def create_echelon_plot(
    results: StageResults, 
    message_data: Message,
    gc: bool = False
    ) -> Message:

    if not gc:
        data = results.stage_points[-1]
        match_name = data.loc[data['MATCH'].notna(), 'MATCH'].unique()[0]
        file_name = os.path.join(PATH_RESULTS, f"{match_name.lower()}_plot.png")
    else: 
        data = results.all_points
        match_name = 'Algemeen Klassement'
        file_name = os.path.join(PATH_RESULTS, f"{match_name.lower()}_plot.png")

    gc = pd.DataFrame(data.groupby('COACH')['POINTS'].sum().sort_values(ascending=False))
    gc.reset_index(inplace=True)
    gc['RELATIVE_POSITION'] = (gc['POINTS'] - gc['POINTS'].min())/(gc['POINTS'].max() - gc['POINTS'].min())
    gc['ECHELON'] = (gc['RELATIVE_POSITION'].shift(1) > (gc['RELATIVE_POSITION'] + JITTER_THRESHOLD)).cumsum()
    gc['ECHELON_POSITION'] = gc.groupby('ECHELON').cumcount()
    gc['ECHELON_MAXPOINTS'] = gc['ECHELON'].map(gc.groupby('ECHELON')['POINTS'].max())
    gc['XJITTER'] = 1 + gc['ECHELON_POSITION'] * 0.1
    gc['YJITTER'] = gc['POINTS'].max() - (-gc['POINTS']).argsort()*((gc['POINTS'].max() - gc['POINTS'].min())/(gc['COACH'].nunique()-1))

    coach_hue_order = gc.loc[gc['COACH'].str.lower().argsort(), 'COACH'].values

    f = plt.figure(figsize=(512/DPI,720/DPI), dpi=DPI, edgecolor=None)
    sns.scatterplot(
        data=gc, 
        x='XJITTER', 
        y='POINTS', 
        hue='COACH', 
        hue_order=coach_hue_order, 
        palette='colorblind',
        ax=plt.gca())

    palette = sns.color_palette('colorblind', n_colors=gc.shape[0])
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
    plt.title(match_name, fontdict={'size':1.25*FONTSIZE, 'weight':'bold'})

    ax = plt.gca()
    ax.get_legend().remove()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    f.savefig(file_name, bbox_inches='tight', orientation='portrait')

    plt.close(f)

    if strtobool(os.getenv('IMGUR_UPLOAD')):
        img_url = imgur_robot.upload_to_imgur(file_name)
        message_data.img_urls.append(img_url)
    else:
        print(f"No image uploaded; IMGUR_UPLOAD set to {os.getenv('IMGUR_UPLOAD')}")

    return message_data



def create_teams_message(data: pd.DataFrame) -> str:

    data['POINTS_STR'] = data['POINTS'].fillna(0).astype(int).astype(str)
    dfg1 = data.groupby(['COACH', 'RIDER'], as_index=False)['POINTS_STR'].apply(lambda x: '-'.join(x))
    dfg2 = data.groupby(['COACH', 'RIDER'])['POINTS'].sum()
    dfg = dfg1.join(dfg2, on=['COACH', 'RIDER'])

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


def create_forum_message(results_data: StageResults, message_data: Message) -> str:

    teams_message = create_teams_message(results_data.all_points)
    image_message = create_image_string(message_data.img_urls)
    mentions_message = create_mention_string(message_data.coach_mentions)

    return image_message + mentions_message + teams_message

