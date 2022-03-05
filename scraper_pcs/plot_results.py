import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

JITTER_THRESHOLD = 0.08
FONTSIZE = 8
DPI=200

def create_echelon_plot(data: pd.DataFrame, match_name: str, file_name:str) -> None:
    gc = pd.DataFrame(data.groupby('COACH')['POINTS'].sum().sort_values(ascending=False))
    gc.reset_index(inplace=True)
    gc['RELATIVE_POSITION'] = (gc['POINTS'] - gc['POINTS'].min())/(gc['POINTS'].max() - gc['POINTS'].min())
    gc['ECHELON'] = (gc['RELATIVE_POSITION'].shift(1) > (gc['RELATIVE_POSITION'] + JITTER_THRESHOLD)).cumsum()
    gc['ECHELON_POSITION'] = gc.groupby('ECHELON').cumcount()
    gc['ECHELON_MAXPOINTS'] = gc['ECHELON'].map(gc.groupby('ECHELON')['POINTS'].max())
    gc['XJITTER'] = 1 + gc['ECHELON_POSITION'] * 0.1
    gc['YJITTER'] = gc['ECHELON_MAXPOINTS'] - FONTSIZE*gc['ECHELON_POSITION']

    coach_hue_order = gc.loc[gc['COACH'].str.lower().argsort(), 'COACH'].values

    f = plt.figure(dpi=DPI, edgecolor=None)
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
