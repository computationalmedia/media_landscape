'''
Figure 7 in the paper.

Input data:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_prediction/uid_to_leaning_lp.pickle
        output by `Sec_4_2_Label_Spreading/8_label_spreading_prediction.py`
    
    Data/Sec_4_3_URL_Extraction/URLs/processed/{country}.csv
        output by `Sec_4_3_URL_Extraction/4_url_processing.py`
        
Output:
    Plots/correlation_with_United States_fletcher.pdf
    Plots/correlation_with_United Kingdom_fletcher.pdf
    Plots/correlation_with_Australia_fletcher.pdf
    Plots/correlation_with_Germany_fletcher.pdf
    Plots/correlation_with_Spain_fletcher.pdf
    Plots/correlation_with_France_fletcher.pdf
        where country is from US, UK, Australia, Germany Spain and France
        figure 7 in the paper 
    
Usage:
    `python Sec_5_3_Media_Domain_Bias/4_figure_7.py`

'''


############ replace the path below ############

retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'
retweet_net_path = '/Users/caiyang/Documents/_Honours/results/Geoparsed_results/User_Retweet_with_Politician'
url_path = 'Data/Sec_4_2_Label_Spreading/URLs/'
url_path = '/Users/caiyang/Documents/_Honours/results/Geoparsed_results/URLs'
figure_savepath = 'Plots/' 

############ replace the path above ############

import pandas as pd
import numpy as np
import pickle
import up
import seaborn as sns
from scipy.stats import pearsonr

from utils.domain_bias_from_fletcher import *

# rearange the order of countries to match the order they appear in existing_domain_bias_from_fletcher.py
all_countries= ["Australia", "Germany", "Spain", "France", "Ireland", 
                "Italy", "Netherlands", "Poland", "United Kingdom", "United States"]

countries_to_skip = ["Italy", "Ireland", "Netherlands", "Poland", ]


for idx, country in enumerate(all_countries):
    if country in countries_to_skip:
        continue
        
    outlet = outlet_all[idx]
    scores = scores_all[idx]
    
    outlet = outlet.split("\n")
    outlet = { tmp.split(':')[0].strip() : tmp.split(':')[1].strip() for tmp in outlet if tmp.strip() != '' }
    scores = [ float(i) for i in scores.split("\n") if i.strip() != '' ]
    
    fletcher_outlet_scores = dict(zip(list(outlet.values()), scores))

    df = pd.read_csv(f'{url_path}/Processed/{country}.csv')
    df['uid'] = df['uid'].astype(str)
    df = df[~df.links_recons.isin(['twitter'])]
    
    filepath = f"{retweet_net_path}/Country_Network/{country}/"
    with open(f"{filepath}/lp_prediction/uid_to_leaning_lp.pickle", 'rb') as handle:
        uid_to_leaning_lp = pickle.load(handle)
    
    df = df[df.uid.isin(uid_to_leaning_lp)]
    
    sharing_cnt = df[['tweet_id', 'links_recons']].groupby(['links_recons'], as_index=False).nunique()
    sharing_cnt = sharing_cnt.sort_values('tweet_id', ascending=False)
    twitter_link= set( sharing_cnt[sharing_cnt.tweet_id>=50].links_recons.unique() )
    df = df[df.links_recons.isin(twitter_link)]
    
    fletcher_outlet = set( fletcher_outlet_scores.keys() ) 
    our_domains = set( df.links_recons.unique() )
    
    domains_overlap = fletcher_outlet & our_domains
    
    print(f"{country}: {len(outlet)}({len(fletcher_outlet)}); {len(domains_overlap)}; {len(domains_overlap)/len(fletcher_outlet)}")
    print(f"not in: {fletcher_outlet-our_domains}")
    scores = [ fletcher_outlet_scores[overlap_dom] for overlap_dom in domains_overlap ]
    
    df = df[df.links_recons.isin(domains_overlap)]
    domain_uids = df[['uid', 'links_recons']].groupby(['links_recons'], as_index=False).agg(set)
    domain_uids['score'] = domain_uids.uid.apply(lambda x:  np.mean([  uid_to_leaning_lp[x_id] for x_id in x ])*2-1 )

    our_domain_to_score = dict(zip(domain_uids.links_recons, domain_uids.score))
    our_scores = [ our_domain_to_score[overlap_dom] for overlap_dom in domains_overlap ]
    
    pearsonr_res = pearsonr(our_scores, scores)
    
    print(f"{country}: {pearsonr_res}")
    
    score_df = pd.DataFrame( {'Ours': our_scores, f"{country}": scores} )
    g = sns.JointGrid(data=score_df, x=f"{country}", y="Ours", xlim=[-0.5, 0.5], ylim=[-1.0, 1.0])
    g.plot_joint(sns.regplot, line_kws={"color": "red"}, scatter_kws={'s': 4, 'color': '#7aaef5'} )
    g.plot_marginals(sns.kdeplot, color="black", alpha=1, lw=1, bw=.2, clip=(-1,1), )

    ax = g.ax_marg_x   
    x, y = ax.get_lines()[0].get_data()

    ax.margins(x=0)

    kde_x, kde_y = ax.lines[0].get_data()

    ax.fill_between(kde_x, kde_y, where=(kde_x<=0.001), interpolate=True, color='#91BFFF')
    ax.fill_between(kde_x, kde_y, where=(kde_x>=-0.001), interpolate=True, color='#f56149')

    ax.vlines(0.0, 0, np.round(kde_y[np.abs(kde_x).argmin()])+1, color='black')
    ax.axis('off')

    ax = g.ax_marg_y
    x, y = ax.get_lines()[0].get_data()

    kde_x, kde_y = ax.lines[0].get_data()


    ax.fill_betweenx(kde_y, kde_x, where=(kde_y<=0.001), interpolate=True, color='#91BFFF')
    ax.fill_betweenx(kde_y, kde_x, where=(kde_y>=-0.001), interpolate=True, color='#f56149')
    ax.axis('off')

    ax.hlines(0.0, 0, np.round(kde_x[np.abs(kde_y).argmin()])+1, color='black')
    
    g.ax_joint.tick_params(axis='both', which='major', labelsize=20)
    g.ax_joint.tick_params(axis='both', which='minor', labelsize=20)
    
    
    ax = g.ax_joint
    ax.tick_params(axis='both', which='major', labelsize=20)
    ax.tick_params(axis='both', which='minor', labelsize=20)

    ax.set_xlabel(f"{country}",  fontsize=22)
    ax.set_ylabel("Average Audience Leaning Score",  fontsize=22)
    
    fig_savepth = f"{figure_savepath}/correlation_with_{country}_fletcher.pdf"
    g.figure.savefig(fig_savepth, facecolor=(1.0,1.0,1.0,1.0), bbox_inches='tight', dpi=100)

    