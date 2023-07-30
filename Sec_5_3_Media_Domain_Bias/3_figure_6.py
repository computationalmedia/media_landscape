'''
Figure 6 in the paper.

Input data:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/United States/lp_prediction/uid_to_leaning_lp.pickle
        output by `Sec_4_2_Label_Spreading/8_label_spreading_prediction.py`
    
    Data/Sec_4_2_Label_Spreading/URLs/Processed/United States.csv
        output by `Sec_4_3_URL_Extraction/4_url_processing.py`
        
    
Output:
    Plots/correlation_with_Roberson et al Bias Score.pdf
    Plots/correlation_with_Facebook Bias Score.pdf
    Plots/correlation_with_MTurk Bias Score.pdf
    Plots/correlation_with_Budak et al Bias Score.pdf
    Plots/correlation_with_AllSides Patented Bias Score.pdf
    Plots/correlation_with_Pew Bias Score.pdf
        figure 6 in the paper
        
Usage:
    `python Sec_5_3_Media_Domain_Bias/3_figure_6.py`

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
import seaborn as sns
import up

from scipy.stats import pearsonr, spearmanr

from utils.domain_bias_from_robertson import domain_to_rob, domain_to_fb, domain_to_mturk, domain_to_budak, domain_to_allsides, domain_to_pew


basepath = f"{retweet_net_path}/Country_Network/United States/lp_prediction"

with open(f"{basepath}/uid_to_leaning_lp.pickle", 'rb') as handle:
    uid_to_leaning_lp = pickle.load(handle)
    users_present = set( uid_to_leaning_lp.keys() )
    
    
df = pd.read_csv(f'{url_path}/processed/United States.csv')
df['uid'] = df['uid'].astype(str)

df = df[df.uid.isin(uid_to_leaning_lp)]
df = df[~df.links_recons.isin(['twitter' ])]

sharing_cnt = df[['tweet_id', 'links_recons']].groupby(['links_recons'], as_index=False).nunique()
sharing_cnt = sharing_cnt.sort_values('tweet_id', ascending=False)
twitter_link= set( sharing_cnt[sharing_cnt.tweet_id>=50].links_recons.unique() )

labels = ["Roberson et al Bias Score", "Facebook Bias Score", "MTurk Bias Score", 
          "Budak et al Bias Score", "AllSides Patented Bias Score", "Pew Bias Score"]

overlaps = []
original_size = []

for idx, other_score in enumerate([domain_to_rob, domain_to_fb, domain_to_mturk, 
                                   domain_to_budak, domain_to_allsides, domain_to_pew]):
    
    other_domain_recons = set( list(other_score.keys()) )
    domains_overlap = list( twitter_link & other_domain_recons )
    
    overlaps.append(len(domains_overlap))
    original_size.append(len(other_domain_recons))
    
    other_score_list = [ other_score[overlap_dom] for overlap_dom in domains_overlap ]
    
    df_ = df[df.links_recons.isin(domains_overlap)]
    domain_uids = df_[['uid', 'links_recons']].groupby(['links_recons'], as_index=False).agg(set)
    domain_uids['score'] = domain_uids.uid.apply(lambda x:  np.mean([  uid_to_leaning_lp[x_id] for x_id in x ])*2-1 )
    
    our_domain_to_score = dict(zip(domain_uids.links_recons, domain_uids.score))
    our_scores = [ our_domain_to_score[overlap_dom] for overlap_dom in domains_overlap ]
    
    print(len(domains_overlap), np.round(len(domains_overlap)/len(other_domain_recons), 2))
    
    if labels[idx] in ["AllSides", "MTurk"]:
        spearmanr_res = spearmanr(other_score_list, our_scores) 
        print(f"{labels[idx]}: Spearman {spearmanr_res}")
    else:
        pearsonr_res = pearsonr(other_score_list, our_scores) 
        print(f"{labels[idx]}: Pearsonr {pearsonr_res}")
        
    if labels[idx] == "Pew":
        xlim = [-0.5, 0.5]
    elif labels[idx] == "Budak et al":
        xlim = [-0.3, 0.3]
    else:
        xlim = [-1.1, 1.1]
        
    score_df = pd.DataFrame( {'Ours': our_scores, f"{labels[idx]}": other_score_list} )
    g = sns.JointGrid(data=score_df, x=f"{labels[idx]}", y="Ours", xlim=xlim, ylim=[-1.1, 1.1])
    g.plot_joint(sns.regplot, line_kws={"color": "red"}, scatter_kws={'s': 4, 'color': '#7aaef5'} )
    g.plot_marginals(sns.kdeplot, color="black", alpha=1, lw=1, bw=.2, clip=(-1,1), )# palette=cm.get_cmap('coolwarm'))


    ax = g.ax_marg_x   
    x, y = ax.get_lines()[0].get_data()

    ax.margins(x=0)
    ax.set_xlim(xlim)


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
    
    ax.hlines(0.0, 0, np.round(kde_x[np.abs(kde_y).argmin()])+1, color='black')
    ax.axis('off')
        
    g.ax_joint.tick_params(axis='both', which='major', labelsize=20)
    g.ax_joint.tick_params(axis='both', which='minor', labelsize=20)
    
    ax = g.ax_joint
    ax.tick_params(axis='both', which='major', labelsize=20)
    ax.tick_params(axis='both', which='minor', labelsize=20)

    ax.set_xlabel(f"{labels[idx]}",  fontsize=22)
    ax.set_ylabel("Average Audience Leaning Score",  fontsize=22)
        
    
    fig_savepth = f"{figure_savepath}/correlation_with_{labels[idx]}.pdf"
    g.figure.savefig(fig_savepth, facecolor=(1.0,1.0,1.0,1.0), bbox_inches='tight', dpi=100)
