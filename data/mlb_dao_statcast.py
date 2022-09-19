from pybaseball import statcast
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')


def get_batting_stats(season, team):
    return statcast('2019-03-31', '2019-10-04')


# Code for this tutorial was found here https://nkoenig06.github.io/performance-baseball.html
def tutorial():
    hitter_stats = statcast('2019-03-31', '2019-10-04')
    jack_f = hitter_stats[hitter_stats['player_name']=='Jack Flaherty']
    jordan_h = hitter_stats[hitter_stats['player_name']=='Jordan Hicks']

    plt.scatter(jack_f[jack_f['pitch_type']=='FF']['pfx_x'],
            jack_f[jack_f['pitch_type']=='FF']['pfx_z'])

    plt.scatter(jordan_h[jordan_h['pitch_type']=='SI']['pfx_x'],
            jordan_h[jordan_h['pitch_type']=='SI']['pfx_z'])

    hit = hitter_stats[['launch_angle',
        'launch_speed',
        'hc_x',
        'hx_y',
        'if_fielding_alignment',
        'of_fielding_alignment',
        'outs_when_up',
        'home_team',
        'stand',
        'hit_location',
        'p_throws',
        'type',
        'events']]

    in_play = hit[hit['type']=='X']

    in_play['hit'] = in_play['events'].apply(lambda x: 1 if x in('single','double','home_run','triple') else 0)

    print('hardest hit ball: ',in_play['launch_speed'].max())
    print('hardest hit ball: ',in_play['launch_speed'].min())

    # Recodes
    in_play['right_handed_batter'] = np.where(in_play['stand'].values =="R",1,0)
    in_play['right_handed_pitcher'] = np.where(in_play['p_throws'].values =="R",1,0)

    # Drop all variables that will be recoded or dummy coded
    in_play_new = in_play.drop(['if_fielding_alignment',
        'of_fielding_alignment',
        'home_team',
        'stand',
        'type',
        'events',
        'p_throws'],
        axis=1)






