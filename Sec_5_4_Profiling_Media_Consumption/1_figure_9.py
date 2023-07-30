'''
Figure 9 in the paper

Input data:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_prediction/uid_to_leaning_lp.pickle
        output by `Sec_4_2_Label_Spreading/8_label_spreading_prediction.py`
    
    Data/Sec_4_3_URL_Extraction/URLs/processed/{country}.csv
        output by `Sec_4_3_URL_Extraction/4_url_processing.py`
        
Output:
    Plots/country_centric_view_{country}.pdf
        for all 8 countries
        
Example usage:
    `python Sec_5_4_Profiling_Media_Consumption/1_figure_8.py`
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

from utils.config import SELECTED_COUNTRIES
from utils.mbfc_allsides_ideo import get_domain_mbfc_ideo, get_domain_allsides_ideo


country_to_topk_domains = {}
country_to_aud_leaning = {}
country_to_topk_domains_users = {}

for country_idx, country in enumerate(SELECTED_COUNTRIES):
        
    savepath = f'{url_path}/Processed/{country}.csv'
    df = pd.read_csv(savepath)
    df['uid'] = df['uid'].astype(str)
    
    df = df[~df.links_recons.isin( ['twitter'] )]
    
    filepath = f"{retweet_net_path}/Country_Network/{country}/"
    with open(f"{filepath}/lp_prediction/uid_to_leaning_lp.pickle", 'rb') as handle:
        uid_to_leaning_lp = pickle.load(handle)
    
    df = df[df.uid.isin(uid_to_leaning_lp)]
    
    url_ranks = df[['uid', 'links_recons']].groupby(['links_recons'], as_index=False).nunique()
    url_ranks = url_ranks.sort_values('uid', ascending=False).iloc[:15, :]
    
    topk_domains = url_ranks.links_recons.values
    
    topk_domains_aud_leaning_list = []
    topk_domains_aud_leaning = []
    topk_domains_to_user_cnt = []
    
    for top_domain in topk_domains:
    
        domain_users = set( df[df.links_recons == top_domain].uid.unique() )
        
        topk_domains_to_user_cnt.append( len(domain_users) )
        domain_user_leaning_ = [ uid_to_leaning_lp[uid]*2 - 1 for uid in domain_users ]
    
        target_domains_aud_leaning = np.mean( domain_user_leaning_ )
        topk_domains_aud_leaning.append( target_domains_aud_leaning )
        
        topk_domains_aud_leaning_list.append( domain_user_leaning_ )
        
        errors = 1.96 * np.std(domain_user_leaning_) / len(domain_user_leaning_)
    
    topk_domains_aud_leaning = np.array(topk_domains_aud_leaning)
    topk_domains_aud_leaning_list = np.array(topk_domains_aud_leaning_list)
    topk_domains_to_user_cnt = np.array(topk_domains_to_user_cnt)
    
    argidx = np.argsort(topk_domains_aud_leaning)
    topk_domains = topk_domains[argidx]
    topk_domains_aud_leaning = topk_domains_aud_leaning[argidx]
    topk_domains_aud_leaning_list = topk_domains_aud_leaning_list[argidx]
    topk_domains_to_user_cnt = topk_domains_to_user_cnt[argidx]
    
    country_to_topk_domains[country] = topk_domains
    country_to_aud_leaning[country] = topk_domains_aud_leaning_list
    country_to_topk_domains_users[country] = topk_domains_to_user_cnt
   
   
   

for country_idx, country in enumerate(SELECTED_COUNTRIES):
        
    topk_domains = country_to_topk_domains[country]
    topk_domains_padded = [i.rjust(31, ' ') for i in topk_domains]
    topk_domains_aud_leaning_list = country_to_aud_leaning[country]
    topk_domains_to_user_cnt = country_to_topk_domains_users[country]
    
    fig = plt.figure(figsize=(15, 9))
    gs = fig.add_gridspec(nrows=15, ncols=2, wspace=0.5, hspace=0.)
    
    max_y = 0
    for subfig_idx in range(15):
        ax = fig.add_subplot(gs[subfig_idx, 0])
        sns.kdeplot(data=topk_domains_aud_leaning_list[subfig_idx], clip=(-1, 1), bw_adjust=1.0, 
                    fill=False, alpha=1, lw=1, bw=.2, color="black", ax=ax)
        
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
        ax.set_yticks([])
        ax.set_yticklabels([])
        ax.set_ylabel("")
        ax.text(-1.05, 0.3, s=topk_domains_padded[subfig_idx], ha='right', fontsize=32, )
                
        if subfig_idx != 14:
            ax.set_xticks([])
            ax.set_xticklabels([])
            ax.spines['bottom'].set_visible(False)
            
        else:
            ax.set_xlabel("Audience Leaning",  fontsize=36)
            plt.xticks(np.arange(-1, 1.5, 1), [-1.0, 0.0, 1.0], fontsize=32)
            
        x, y = ax.get_lines()[0].get_data()
        segments = np.array([x[:-1], y[:-1], x[1:], y[1:]]).T.reshape(-1, 2, 2)
        norm = plt.Normalize(-1, 1)

        ax.margins(x=0)
        ax.set_ylim(ymin=0, ymax=np.max(y)+0.3)

        ax.fill_between(x, y, where=(x<0.), interpolate=False, color='#348ABD')
        ax.fill_between(x, y, where=(x>0.), interpolate=False, color='#E24A33')
        
        data_mean = np.mean(topk_domains_aud_leaning_list[subfig_idx])
        data_median = np.median(topk_domains_aud_leaning_list[subfig_idx])
        ax.vlines(data_mean, 0, max(y), color='black', linestyles='solid')
        
        max_y = max(max_y, np.max(y) )
    

    
    topk_domain_mbfc_ideos = get_domain_mbfc_ideo(topk_domains)
    topk_domain_allsides_ideos = get_domain_allsides_ideo(topk_domains)
    topk_domains_comb_ideos = [ f"{topk_domain_mbfc_ideos[_idx]}, {topk_domain_allsides_ideos[_idx]}" \
                                for _idx in range(len(topk_domains)) ]

    
    for subfig_idx in range(15):
        ax = fig.add_subplot(gs[subfig_idx, 1])
        bars = ax.barh([0], topk_domains_to_user_cnt[subfig_idx]/1000, color='#047994', 
                       edgecolor='black', linewidth=1.5, fill=False, height=0.1)

        
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
        ax.set_yticks([0])
        ax.set_yticklabels([topk_domains_comb_ideos[subfig_idx]], rotation=0, fontsize=32, ha='right')
        ax.set_ylabel("")
        
        ax.set_xlim(0, np.ceil(max(topk_domains_to_user_cnt)/1000) )

        ax.set_ylim(-0.1, 0.1)
        
        if subfig_idx != 14:
            ax.set_xticks([])
            ax.set_xticklabels([])
            ax.spines['bottom'].set_visible(False)
    
        else:
            xticks = ax.get_xticks()
            
            xticklabels = ['0']
            for tick in xticks[1:]:
                if int(tick) == tick:
                    xticklabels += [f"{int(tick)}k"]
                else:
                    xticklabels += [""]
            
            if "" not in xticklabels:
                tick_length = len(xticklabels)
                for i in range(2, len(xticklabels), 2):
                    xticklabels[i] = ''

            plt.xticks(xticks, xticklabels, fontsize=32)
            
            ax.set_xlabel("$\kappa$",  fontsize=36)
    
    plt.suptitle(f"{country}", fontsize=38)
    fig.subplots_adjust(top=0.92, bottom=0.1,)
    
    fig.tight_layout()
            
    fig_savepth = f"{figure_savepath}/country_centric_view_{country}.pdf"
    fig.savefig(fig_savepth, bbox_inches = 'tight', facecolor=(1.0,1.0,1.0,1.0), dpi=100)

