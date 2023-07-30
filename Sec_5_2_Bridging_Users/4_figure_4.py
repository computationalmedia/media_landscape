'''
Figure 4 in the paper

Input data:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/uid_to_leaning_lp.pickle 
        output by `Sec_4_2_Label_Spreading/8_label_spreading_prediction.py`
    Data/Sec_4_2_Label_Spreading/retweet_net_global/Bridging_Users/Leaning_Estimate/{cali_country}_{anchor_country}.pickle 
        output by `3_label_spreading_with_bridging_users.py`
    
Output:
    Plots/Bridging_Users_{country}.pdf for seven countries, excluding US.
        figure 4 density plots in the paper
        
Usage:
    `python Sec_5_2_Bridging_Users/4_figure_4.py`
'''



############ replace the path below ############

retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'
figure_savepath = 'Plots/'

############ replace the path above ############


import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import up

from scipy.stats import pearsonr

from utils.config import SELECTED_COUNTRIES

anchor_country = 'United States'

filepath = f"{retweet_net_path}/Country_Network/{anchor_country}/"

with open(f"{filepath}/lp_prediction/uid_to_leaning_lp.pickle", 'rb') as handle:
    anchor_original_leaning = pickle.load(handle)
        


# first obtain the leaning scores for bridging users for within-country network and after calibration
country_to_bridging_scores = dict()

for cali_country in SELECTED_COUNTRIES[1:]:
    
    filepath = f'{retweet_net_path}/Bridging_Users/Leaning_Estimate'
    with open(f"{filepath}/{cali_country}_{anchor_country}.pickle", 'rb') as handle:
        cali_mapped_leaning = pickle.load(handle)

    filepath = f"{retweet_net_path}/Country_Network/{cali_country}/"
    with open(f"{filepath}/lp_prediction/uid_to_leaning_lp.pickle", 'rb') as handle:
        cali_original_leaning = pickle.load(handle)
        
    bridging_users_cali_to_anchor = set( cali_mapped_leaning.keys() ) & set( cali_original_leaning.keys() )
    print(f"\n{cali_country}-{anchor_country}: bridging_users: ", len(bridging_users_cali_to_anchor))
    
    leaning_pairs = []
    for user in bridging_users_cali_to_anchor:
        calibrated_leaning = cali_mapped_leaning[user]
        original_leaning = cali_original_leaning[user]
        leaning_pairs.append( [original_leaning, calibrated_leaning] )
    
    
    filepath = f'{retweet_net_path}/Bridging_Users/Leaning_Estimate'
    with open(f"{filepath}/{anchor_country}_{cali_country}.pickle", 'rb') as handle:
        anchor_mapped_leaning = pickle.load(handle)
    
    bridging_users_anchor_to_cali = set( anchor_mapped_leaning.keys() ) & set( anchor_original_leaning.keys() )

    for user in bridging_users_anchor_to_cali:
        calibrated_leaning = anchor_mapped_leaning[user]
        original_leaning = anchor_original_leaning[user]
        leaning_pairs.append( [calibrated_leaning, original_leaning] )
    
    
    leaning_pairs = np.array(leaning_pairs)

    print(f"{cali_country} before and after: { pearsonr(leaning_pairs[:, 0], leaning_pairs[:, 1]) }")

    country_to_bridging_scores[cali_country] = leaning_pairs
    
    
    
# get some text annotation before
country_to_colobar_annot = {}

for cali_country in SELECTED_COUNTRIES[1:]:

    leaning_pairs = country_to_bridging_scores[cali_country]
    leaning_pairs = leaning_pairs*2 - 1
    user_size = leaning_pairs.shape[0]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    sns.kdeplot(
        data=leaning_pairs, x=leaning_pairs[:, 0], y=leaning_pairs[:,1], fill=True, ax=ax,
        color=(210/255, 191/255, 202/255), clip=(-1, 1), cbar=True, 
    )
    
    pos_to_annotate, text_to_annotate = [], []
    for colorbar_text in ax.figure.axes[-1].get_yticklabels():
        ypos = colorbar_text.get_position()[1]
        text = colorbar_text.get_text()
        text_to_annotate.append(text)
        pos_to_annotate.append(ypos)
    
    
    if cali_country != 'Turkey':
        pos_to_annotate = [ pos_to_annotate[i] for i in range(0, len(pos_to_annotate), 3) ]
        text_to_annotate = [ float(text_to_annotate[i]) for i in range(0, len(text_to_annotate), 3) ]
    else:
        pos_to_annotate = [ pos_to_annotate[i] for i in [0,4,7,9]]
        text_to_annotate = [ float(text_to_annotate[i]) for i in [0,4,7,9]]
    
    country_to_colobar_annot[cali_country] = text_to_annotate
    
# we do some manual editing here
text_to_annotate = country_to_colobar_annot['United Kingdom']
text_to_annotate[0] += 0.0005
text_to_annotate[-1] -= 0.0005

text_to_annotate = country_to_colobar_annot['Australia']
text_to_annotate[0] += 0.0005
text_to_annotate[-1] -= 0.0005

text_to_annotate = country_to_colobar_annot['France']
text_to_annotate[0] += 0.0005

text_to_annotate = country_to_colobar_annot['Germany']
text_to_annotate[-1] -= 0.0005

text_to_annotate = country_to_colobar_annot['Turkey']
text_to_annotate[-1] -= 0.0005


# plot here
for cali_country in SELECTED_COUNTRIES[1:]:

    leaning_pairs = country_to_bridging_scores[cali_country]
    leaning_pairs = leaning_pairs*2 - 1
    user_size = leaning_pairs.shape[0]
    
    cbar_ticks = country_to_colobar_annot[cali_country]

    fig = plt.figure(figsize=(6,5))
    ax = fig.add_subplot(111)

    sns.kdeplot(
        data=leaning_pairs, x=leaning_pairs[:, 0], y=leaning_pairs[:,1], fill=True, ax=ax,
        color=(210/255, 191/255, 202/255), clip=(-1, 1), cbar=True, n_levels=10,
        shade_lowest=False, cbar_kws = {'format': "%.1f", "ticks": cbar_ticks }
    )
    
    ax.set_xlabel(f"{cali_country}\nN={user_size}", fontsize=24)
    ax.set_ylabel("United States", fontsize=24)
    
    ax.tick_params(axis='both', which='major', labelsize=22)
    ax.tick_params(axis='both', which='minor', labelsize=22)
    
    ax.figure.axes[-1].tick_params(labelsize=22)


    fig_savepth = f"{figure_savepath}/Bridging_Users_{cali_country}.pdf"
    fig.savefig(fig_savepth, bbox_inches='tight', facecolor=(1.0,1.0,1.0,1.0), dpi=300)
