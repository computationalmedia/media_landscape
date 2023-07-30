'''
Figure 10 in the paper

Input data:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_prediction/uid_to_leaning_lp.pickle
        output by `Sec_4_2_Label_Spreading/8_label_spreading_prediction.py`
        
    Data/Sec_4_3_URL_Extraction/URLs/processed/{country}.csv
        output by `Sec_4_3_URL_Extraction/4_url_processing.py`
        
Output:
    Plots/media_centric_view_{dom}.pdf
        for a list of given domains
        
Example usage:
    `python Sec_5_4_Profiling_Media_Consumption/2_figure_9.py`
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
import matplotlib.pyplot as plt
import seaborn as sns
import up

from utils.config import SELECTED_COUNTRIES, SELECTED_DOMAINS
from utils.mbfc_allsides_ideo import get_domain_mbfc_ideo, get_domain_allsides_ideo


target_dom_to_aud_leaning = { domain: [] for domain in SELECTED_DOMAINS }
target_dom_to_user_cnt = { domain: [] for domain in SELECTED_DOMAINS }
target_dom_to_aud_leaning_list = { domain: [] for domain in SELECTED_DOMAINS }


for country_idx, country in enumerate(SELECTED_COUNTRIES):
        
    savepath = f'{url_path}/Processed/{country}.csv'
    df = pd.read_csv(savepath)
    df['uid'] = df['uid'].astype(str)
    
    df = df[~df.links_recons.isin( ['twitter'] )]
    
    filepath = f"{retweet_net_path}/Country_Network/{country}/"
    with open(f"{filepath}/lp_prediction/uid_to_leaning_lp.pickle", 'rb') as handle:
        uid_to_leaning_lp = pickle.load(handle)
    
    df = df[df.uid.isin(uid_to_leaning_lp)]
    df = df[df.links_recons.isin(SELECTED_DOMAINS)]

    for target_dom in SELECTED_DOMAINS:
    
        domain_users = set( df[df.links_recons == target_dom].uid.unique() )
        target_dom_to_user_cnt[target_dom].append(len(domain_users))
        
        domain_user_leaning_ = [ uid_to_leaning_lp[uid]*2 - 1 for uid in domain_users ]
        
        target_dom_to_aud_leaning_list[target_dom].append( domain_user_leaning_ )
        
        target_domains_aud_leaning = np.mean( domain_user_leaning_ )        
        target_dom_to_aud_leaning[target_dom].append( target_domains_aud_leaning )
                

for plot_idx, dom in enumerate(SELECTED_DOMAINS):
    
    domain_aud_leaning = np.array( target_dom_to_aud_leaning[dom] )
    domain_aud_leaning_list = np.array( target_dom_to_aud_leaning_list[dom] )
    domains_to_user_cnt = np.array( target_dom_to_user_cnt[dom] )

    country_list_ = np.array(SELECTED_COUNTRIES)

    
    fig = plt.figure(figsize=(12, 10))
    gs = fig.add_gridspec(nrows=8, ncols=2, wspace=0.1, hspace=.0)
    
    for subfig_idx in range(len(SELECTED_COUNTRIES)):
        ax = fig.add_subplot(gs[subfig_idx, 0])
        sns.kdeplot(data=domain_aud_leaning_list[subfig_idx], clip=(-1, 1),
                    fill=False, alpha=1, lw=1, bw=.2, color="black", ax=ax)
        
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
        ax.set_yticks([])
        ax.set_yticklabels([])
        ax.set_ylabel("")
        ax.text(-1.05, 0.3, s=country_list_[subfig_idx], ha='right', fontsize=24, )

        
        if subfig_idx != len(SELECTED_COUNTRIES)-1:
            ax.set_xticks([])
            ax.set_xticklabels([])
            ax.spines['bottom'].set_visible(False)
            
        else:
            ax.set_xlabel("Audience Leaning",  fontsize=26)
            plt.xticks(np.arange(-1, 1.5, 0.5), [-1.0, -0.5, 0.0, 0.5, 1.0], fontsize=24)
            
        x, y = ax.get_lines()[0].get_data()
        segments = np.array([x[:-1], y[:-1], x[1:], y[1:]]).T.reshape(-1, 2, 2)
        norm = plt.Normalize(-1, 1)

        ax.margins(x=0)
        ax.set_ylim(ymin=0)

        ax.fill_between(x, y, where=(x<0), interpolate=False, color='#348ABD')
        ax.fill_between(x, y, where=(x>-0.002), interpolate=False, color='#E24A33')
        
        data_mean = np.mean(domain_aud_leaning_list[subfig_idx])
        data_median = np.median(domain_aud_leaning_list[subfig_idx])
        ax.vlines(data_mean, 0, max(y), color='black', linestyles='solid')

        ax.set_xlim(-1.0, 1.0)
            
    for subfig_idx in range(len(SELECTED_COUNTRIES)):
        ax = fig.add_subplot(gs[subfig_idx, 1])
        bars = ax.barh([0], np.log10(domains_to_user_cnt[subfig_idx]), color='#047994', 
                       edgecolor='black', linewidth=1.5, fill=False, height=0.1)

        
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
        ax.set_yticks([])
        ax.set_yticklabels([])
        ax.set_ylabel("")
        
        ax.set_xlim(0, np.ceil(max(np.log10(domains_to_user_cnt)) ) )
        ax.set_ylim(-0.1, 0.1)
        
        if subfig_idx != len(SELECTED_COUNTRIES)-1:
            ax.set_xticks([])
            ax.set_xticklabels([])
            ax.spines['bottom'].set_visible(False)
    
        else:
            xticks = ax.get_xticks()
            print("xticks: ", xticks)
            plt.xticks(xticks, [str(int(i)) for i in xticks], fontsize=24 )

            ax.set_xlabel("$\log_{10}(\kappa)$", fontsize=26)
    
    
    dom_mbfc_ideo = get_domain_mbfc_ideo([dom])[0]
    dom_allsides_ideo = get_domain_allsides_ideo([dom])[0]
    title = f"{dom} ({dom_mbfc_ideo.strip()}, {dom_allsides_ideo.strip()})"

        
    plt.suptitle(f"{title}", fontsize=30)
    fig.subplots_adjust(top=0.94, bottom=0.1,)
    
    fig_savepth = f"{figure_savepath}/media_centric_view_{dom}.pdf"
    fig.savefig(fig_savepth, bbox_inches = 'tight', facecolor=(1.0,1.0,1.0,1.0), dpi=300)
