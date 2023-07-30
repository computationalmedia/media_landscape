'''
Plot figure 1 in the paper.

Input data:
    Data/Sec_3_COVID2020/stats/{start_date}_to_{end_date}.pickle
        output by `dataset_stats.py`
        
Output:
    Plots/covid2020_stats.pdf
        figure 1 in the paper

Usage:
    `python Sec_3_COVID2020/3_figure_1.py`
'''

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt


############ replace the path below ############

# path to extracted dataset stats, i.e. output from `2_dataset_stats.py`
stats_path = 'Data/Sec_3_COVID2020/stats/'
fig_savepth = 'Plots/'

############ replace the path above ############


x_axis_dates = []
our_tweets = []
kris_tweets = []
overlap_ratio = []

daily_ours = []

for file in sorted(os.listdir(stats_path)):
    if file.endswith('.DS_Store'):
        continue
    with open(f"{stats_path}/{file}", "rb") as f:
        stats = pickle.load(f)
        dates = list( stats.keys() )
        start_date = dates[0].split('/')[-1].split('.')[0].split('-', 1)[-1]
        end_date = dates[-1].split('/')[-1].split('.')[0].split('-', 1)[-1]
        
        weekly_out_total_tweet = sum( [ info['our_total_tweet'] for info in stats.values() ] ) / len(dates)
        weekly_kris_total_tweet = sum( [ info['kristina_total_tweet'] for info in stats.values() ] ) / len(dates)
        weekly_overlap_ratio_ours = sum( [ info['overlap_ratio_ours'] for info in stats.values() ] ) / len(dates)
        weekly_overlap_ratio_kris = sum( [ info['overlap_ratio_kris'] for info in stats.values() ] ) / len(dates)
        
        daily_ours += [ info['our_total_tweet'] for info in stats.values() ]
        
        x_axis_dates.append( f"{start_date} - {end_date}" )
        our_tweets.append( weekly_out_total_tweet/1000000 )
        kris_tweets.append( weekly_kris_total_tweet/1000000 )
        overlap_ratio.append( weekly_overlap_ratio_kris )
                

# note: due to the two missing periods in our COVID2020 dataset,
# the following numbers 4.28291, 4.031726 are added manually
# these numbers can be obtained by summing over the numer of tweets from the corresponding period in Chen et al
# didn't do it here to for simplicity
full_dates = x_axis_dates[:7] + ['06-29 - 07-05', '07-13 - 07-19'] + x_axis_dates[7:]
our_tweets_full = our_tweets[:7] + [np.nan, np.nan] + our_tweets[7:]
kris_tweets_full = kris_tweets[:7] + [4.28291, 4.031726] + kris_tweets[7:]


overlap_ratio_100 = [ 100*i for i in overlap_ratio ]
overlap_ratio_full = overlap_ratio_100[:7] + [0, 0] + overlap_ratio_100[7:]

full_dates = np.arange(13, 49, 2)

fig = plt.figure(figsize=(8, 4))

ax = fig.add_subplot(111)
ax.plot(full_dates, our_tweets_full, label='Our Data', linewidth=3, c='#049456',  marker='o')
ax.plot(full_dates, kris_tweets_full, label="Chen et al.", linewidth=3,  marker='x')


ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3, fancybox=True, shadow=True)


ax.set_xlabel('Week number', fontsize=13)
ax.set_ylabel('Avg. daily tweet volume', fontsize=13)

plt.yticks(list(range(0, 30, 5)), ['0'] + [f'{i}M' for i in range(5, 30, 5)])


plt.grid(False)

plt.tick_params(axis='both', which='major', labelsize=12)


ax2 = ax.twinx()
ax.set_zorder(10)
ax.patch.set_visible(False)

ax2.bar(full_dates, overlap_ratio_full, color='#A39F9F', alpha = 0.4, width=1.0)

ax2.set_ylabel("Coverage of (Chen et al.)", fontsize=12)
plt.yticks(list(range(0, 120, 20)), ['0'] + [f'{i}%' for i in range(20, 120, 20)])

plt.xticks(np.arange(13, 49, 2), np.arange(13, 49, 2), rotation=0)

plt.tick_params(axis='both', which='major', labelsize=12)

fig.savefig(f"{fig_savepth}/covid2020_stats.pdf", bbox_inches='tight', facecolor=(1.0,1.0,1.0,1.0), dpi=300)