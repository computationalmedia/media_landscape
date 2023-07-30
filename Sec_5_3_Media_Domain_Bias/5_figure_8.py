'''
Figure 8 in the paper.
Also prepare the color values based on domain bias scores in US. It will be used for generating figure 5 in the paper.

Input data:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_prediction/uid_to_leaning_lp.pickle
        output by `Sec_4_2_Label_Spreading/8_label_spreading_prediction.py`
    
    Data/Sec_4_3_URL_Extraction/URLs/processed/{country}.csv
        output by `Sec_4_3_URL_Extraction/4_url_processing.py`
        
Output:
    Plots/country_domain_heatmap.pdf
        figure 8 in the paper
    Data/Sec_4_2_Label_Spreading/URLs/domain_to_color_based_on_US.pickle

Usage:
    `python Sec_5_3_Media_Domain_Bias/5_domain_to_bias_color.py`
'''

############ replace the path below ############

retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'
retweet_net_path = '/Users/caiyang/Documents/_Honours/results/Geoparsed_results/User_Retweet_with_Politician'
url_path = 'Data/Sec_4_2_Label_Spreading/URLs/'
url_path = '/Users/caiyang/Documents/_Honours/results/Geoparsed_results/URLs'
figure_savepath = 'Plots/' 

############ replace the path above ############


import numpy as np
import pandas as pd
import pickle
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import seaborn as sns
import up
import colorsys

from collections import defaultdict
from matplotlib.colors import DivergingNorm

from utils.config import SELECTED_COUNTRIES


domain_to_sharings = defaultdict(int)

for country_idx, country in enumerate(SELECTED_COUNTRIES) :
        
    savepath = f'{url_path}/processed/{country}.csv'
    df = pd.read_csv(savepath)
    df = df[~df.links_recons.isin(['twitter', ])]

    sharing_cnt = df[['tweet_id', 'links_recons']].groupby(['links_recons'], as_index=False).nunique()
    sharing_cnt = dict( zip( sharing_cnt.links_recons , sharing_cnt.tweet_id ) )
    
    for link, user_cnt in sharing_cnt.items():
        domain_to_sharings[link] += user_cnt
    
    
domain_to_sharings = dict( sorted(domain_to_sharings.items(), key=lambda x: x[1])[::-1] )

domain_sharing_cnt = list( domain_to_sharings.values() )
domains = list( domain_to_sharings.keys() )

topk = 50

domain_sharing_cnt_to_plot = domain_sharing_cnt[:topk] 
topk_domains = domains[:topk] 


domain_to_users = defaultdict(set)
country_to_domain_sharing = {country: {dom: 0 for dom in topk_domains} for country in SELECTED_COUNTRIES}

for country_idx, country in enumerate(SELECTED_COUNTRIES) :
        
    basepath = f"{retweet_net_path}/Country_Network/{country}/lp_prediction"

    with open(f"{basepath}/uid_to_leaning_lp.pickle", 'rb') as handle:
        uid_to_leaning_lp = pickle.load(handle)
    
    savepath = f'{url_path}/processed/{country}.csv'
    df = pd.read_csv(savepath)
    
    df['uid'] = df['uid'].astype(str)
    
    df = df[df.uid.isin(uid_to_leaning_lp)]
    
    domain_uids = df[['uid', 'links_recons']].groupby(['links_recons'], as_index=False).agg(set)

    domain_to_user_country = dict(zip(domain_uids.links_recons, domain_uids.uid))
    
    if country == 'United States':
        for domain, users in domain_to_user_country.items():
            domain_to_users[domain] |= users

    domain_to_sharing = df[['uid', 'links_recons']].groupby(['links_recons'], as_index=False).nunique()
    domain_to_sharing = dict(zip(domain_to_sharing.links_recons, domain_to_sharing.uid))
    
    total_sharing = df.uid.unique().shape[0] #sum(domain_to_sharing.values())
    domain_to_sharing_norm = {dom : sharing/total_sharing for dom, sharing in domain_to_sharing.items()}
    
    domain_to_sharing_norm = {dom : sharing for dom, sharing in domain_to_sharing_norm.items() if dom in topk_domains}
    country_to_domain_sharing[country].update( domain_to_sharing_norm )
    
    
basepath = f"{retweet_net_path}/Country_Network/United States/lp_prediction"

with open(f"{basepath}/uid_to_leaning_lp.pickle", 'rb') as handle:
    uid_to_leaning_lp = pickle.load(handle)
    
domain_to_bias = {}
for domain, users in domain_to_users.items():
    if domain not in topk_domains:
        continue
    avg_user_bias = np.mean( [ uid_to_leaning_lp[u]*2-1 for u in users ] )
    domain_to_bias[domain] = avg_user_bias
    
domain_rank_by_bias = dict(sorted(domain_to_bias.items(), key=lambda x: x[1]))

data = np.array( [ list(domain_rank_by_bias.values()) ] )
cmap = cm.get_cmap('coolwarm')
norm = DivergingNorm(vmin=data.min(), vcenter=0.0, vmax=data.max())

rgba_values = cmap(norm(data))
rgba_values = rgba_values.squeeze()
rgba_values = rgba_values[:, :3]

domain_to_color = {}
for idx, domain in enumerate(domain_rank_by_bias.keys()):
    
    c = colorsys.rgb_to_hsv(*rgba_values[idx])
    new_rgb = colorsys.hsv_to_rgb(c[0], c[1], 0.5)
    
    domain_to_color[domain] = new_rgb
    
with open(f"{url_path}/domain_to_color_based_on_US.pickle", "wb") as f:
    pickle.dump(domain_to_color, f)
    
    
    
    
country_by_domains = []

for country in SELECTED_COUNTRIES:
    country_to_url = country_to_domain_sharing[country]
    
    country_array = []
    
    for domain in domain_rank_by_bias:
        country_array.append( country_to_url[domain] )
        
    country_by_domains.append(country_array)
    
country_by_domains = np.array(country_by_domains)



x_axis_labels = list(domain_rank_by_bias.keys())
y_axis_labels = SELECTED_COUNTRIES

domain_colors1 = sns.color_palette("crest", n_colors=100)[0:10]
domain_colors2 = sns.color_palette("crest", n_colors=100)[17:100]
fig = plt.figure(figsize=(20, 3))

mask = mask = np.zeros_like(country_by_domains)
mask[ np.round(country_by_domains, 3) == 0 ] = True

ax = sns.heatmap(country_by_domains, cmap=domain_colors2, xticklabels=x_axis_labels, yticklabels=y_axis_labels, 
                 cbar=True, cbar_kws={"pad":0.02, }, linewidths=0.5, mask=mask)

ax.set_facecolor(domain_colors1[0])

for j in range(country_by_domains.shape[1]):

    c = colorsys.rgb_to_hsv(*rgba_values[j])
    new_rgb = colorsys.hsv_to_rgb(c[0], c[1], 0.5)

    plt.gca().get_xticklabels()[j].set_color(new_rgb) 

_ = plt.yticks(fontsize=18) 
_ = plt.xticks(fontsize=15) 
plt.tick_params(axis='both', which='both', length=0)


fig_savepth = f"{figure_savepath}/country_domain_heatmap.pdf"
fig.savefig(fig_savepth, bbox_inches='tight', facecolor=(1.0,1.0,1.0,1.0), dpi=300)
