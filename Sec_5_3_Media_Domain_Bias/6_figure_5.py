'''
Figure 5 in the paper

Input data:
    Data/Sec_4_2_Label_Spreading/URLs/processed/{country}.csv
        output by `Sec_4_3_URL_Extraction/4_url_processing.py`
        
    Data/Sec_4_2_Label_Spreading/URLs/domain_to_color_based_on_US.pickle
        output by `5_figure_8.py`
        
Output:
    Plots/url_sharing_ranking.pdf
    
Usage:
    `python Sec_5_3_Media_Domain_Bias/6_figure_5.py`
'''


############ replace the path below ############

url_path = 'Data/Sec_4_2_Label_Spreading/URLs/'
url_path = '/Users/caiyang/Documents/_Honours/results/Geoparsed_results/URLs'
figure_savepath = 'Plots/' 

############ replace the path above ############


import pickle
import matplotlib.pyplot as plt
import pandas as pd
import up

from collections import defaultdict

from utils.config import SELECTED_COUNTRIES


domain_to_sharings = defaultdict(int)

for country_idx, country in enumerate(SELECTED_COUNTRIES) :
        
    savepath = f'{url_path}/processed/{country}.csv'
    df = pd.read_csv(savepath)
    df = df[~df.links_recons.isin(['twitter'])]

    sharing_cnt = df[['tweet_id', 'links_recons']].groupby(['links_recons'], as_index=False).nunique()
    sharing_cnt = dict( zip( sharing_cnt.links_recons , sharing_cnt.tweet_id ) )
    
    for link, user_cnt in sharing_cnt.items():
        domain_to_sharings[link] += user_cnt
    
    if country == 'United States':
        domain_to_US_sharings = domain_to_sharings.copy()
        

domain_to_sharings = dict( sorted(domain_to_sharings.items(), key=lambda x: x[1])[::-1] )


domain_sharing_cnt = list( domain_to_sharings.values() )
domains = list( domain_to_sharings.keys() )

topk = 50

domain_sharing_cnt_to_plot = domain_sharing_cnt[:topk] 
domains_to_plot = domains[:topk] 

domain_sharing_US_cnt_to_plot = [ domain_to_US_sharings[dom] for dom in domains_to_plot ]


with open(f"{url_path}/domain_to_color_based_on_US.pickle", "rb") as f:
    domain_to_color = pickle.load(f)
    
    
fig = plt.figure(figsize=(20, 5), dpi=300)

ax = fig.add_subplot(111)
plt.grid(axis='y')       


bars = ax.bar(domains_to_plot, domain_sharing_cnt_to_plot, color='#948d91', 
              edgecolor='black', linewidth=1.5, fill=False, label='Global', )


bars = ax.bar(domains_to_plot, domain_sharing_US_cnt_to_plot, color='#b9bec7',
              edgecolor='black', linewidth=1.5, fill=True, label='US', )


for idx, domain in enumerate(domains_to_plot):
    plt.gca().get_xticklabels()[idx].set_color(domain_to_color[domain]) 

    
_ = plt.xticks(rotation=90)
_ = plt.yticks(list(range(0, 800000, 200000)),  ['0']+[f'{i}k' for i in range(200, 800, 200)])

plt.tick_params(axis='both', which='major', labelsize=20)

plt.xlabel('Domain', fontsize=22)
plt.ylabel('Audience Reach', fontsize=22)


plt.legend(facecolor=(1.0,1.0,1.0,1.0), bbox_to_anchor=(0.95, 0.85),  
           frameon=False, ncol=1, prop={'size': 18, }, loc='upper right')#, labelspacing=0.1)

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

plt.grid(False)
plt.xlim(-1, 51)

fig_savepth = f"{figure_savepath}/url_sharing_ranking.pdf"
fig.savefig(fig_savepth, bbox_inches='tight', facecolor=(1.0,1.0,1.0,1.0), dpi=300)