'''
Figure 3 in the paper.

Input data:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_prediction/uid_to_leaning_lp.pickle
        output by `Sec_4_2_Label_Spreading/8_label_spreading_prediction.py`

Output:
    Plots/audience_leaning_ridge_plot_{idx}.pdf
        idx ranges from 0 to 3, 4 figures in total
        figure 3 in the paper
    
Usage:
    `python Sec_5_1_User_Leaning_by_Country/1_figure_3.pdf`
'''


############ replace the path below ############

retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'
figure_savepath = 'Plots/'

############ replace the path above ############



import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
import seaborn as sns

from collections import defaultdict

def ridge_plot(country_to_uid_leaning_subset, group_index):

    all_leaning = []
    all_countries = []

    for idx, (country, audience_score) in enumerate(country_to_uid_leaning_subset.items() ):

        audience_score = [i*2-1 for i in audience_score]
        all_leaning += audience_score
        all_countries += [country] * len(audience_score)

    df = pd.DataFrame( {'Country': all_countries, 'Leaning': all_leaning, } )

    df.loc[df.Country == 'United States', 'Country'] = 'US'
    df.loc[df.Country == 'United Kingdom', 'Country'] = 'UK'

    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

    # Initialize the FacetGrid object
    pal = sns.cubehelix_palette(3, rot=-.25, light=.7)
    g = sns.FacetGrid(df, row="Country", hue="Country", aspect=2.5, height=1.0, #hue_kws=colors,
                    palette=pal, gridspec_kws={"hspace":0.1,}, xlim=[0,1], legend_out=True )


    g.map(sns.kdeplot, "Leaning", clip_on=False, shade=True, alpha=1, lw=1, bw=.2, clip=(-1,1),)
    g.map(sns.kdeplot, "Leaning", clip_on=False, color="black", lw=1, bw=.2, clip=(-1,1), )


    # passing color=None to refline() uses the hue mapping
    g.refline(y=0, linewidth=0.1, linestyle="-", color='black', clip_on=False)

    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label):
        ax = plt.gca()
            
        country_left = country_to_left_leaning_users[label]
        country_total = country_to_users_with_leaning[label]
        left_ratio = np.round(country_left/country_total, 3)
        right_ratio = 1-left_ratio
        
        label_to_plot = label + f"\n{np.round(country_total/1000, 1)}k" + f"\nL={str(100*left_ratio)[:4]}%" + f"\nR={str(100*right_ratio)[:4]}%"
        
        ax.text(-0.5, 0.3, label_to_plot, fontweight="bold", color='#777777', ha="left", va="center", transform=ax.transAxes)

    g.map(label, "Leaning")


    # Remove axes details that don't play well with overlap
    g.set_titles("")
    g.set(yticks=[], ylabel="", xlim=[-1, 1])
    g.despine(bottom=True, left=True)

        
    for ax in g.axes:    
        x, y = ax[0].get_lines()[0].get_data()

        ax[0].margins(x=0)
        ax[0].set_ylim(ymin=0)
        
        ax[0].fill_between(x, y, where=(x<0.), interpolate=False, color='#348ABD')
        ax[0].fill_between(x, y, where=(x>0.), interpolate=False, color='#E24A33')

    fig_savepth = f"{figure_savepath}/audience_leaning_ridge_plot_{group_index}.pdf"
    g.figure.savefig(fig_savepth, bbox_inches='tight', facecolor=(1.0,1.0,1.0,1.0), dpi=300)

if __name__ == "__main__":

    # arange countries in a different order for plotting
    country_list = ['United States', 'Spain', 'United Kingdom', 'France', 'Canada', 'Germany', 'Australia', 'Turkey', ]


    country_to_uid_leaning = {}
    country_to_left_leaning_users = defaultdict(int)
    country_to_users_with_leaning = defaultdict(int)

    for country in country_list:
        
        filepath = f"{retweet_net_path}/Country_Network/{country}/"

        with open(f"{filepath}/lp_prediction/uid_to_leaning_lp.pickle", 'rb') as handle:
            uid_to_leaning_lp = pickle.load(handle)
        
        country_to_uid_leaning[country] = list(uid_to_leaning_lp.values())
        
        for leaning in uid_to_leaning_lp.values():
            if leaning <= 0.5:
                country_to_left_leaning_users[country] += 1
            country_to_users_with_leaning[country] += 1
        

    country_list_1, country_list_2, country_list_3, country_list_4 = country_list[:2], country_list[2:4], country_list[4:6], country_list[6:8]

    country_to_uid_leaning_1 = {c:country_to_uid_leaning[c] for c in country_list_1}
    country_to_uid_leaning_2 = {c:country_to_uid_leaning[c] for c in country_list_2}
    country_to_uid_leaning_3 = {c:country_to_uid_leaning[c] for c in country_list_3}
    country_to_uid_leaning_4 = {c:country_to_uid_leaning[c] for c in country_list_4}

    country_to_left_leaning_users['US'] = country_to_left_leaning_users['United States']
    country_to_left_leaning_users['UK'] = country_to_left_leaning_users['United Kingdom']
    country_to_users_with_leaning['US'] = country_to_users_with_leaning['United States']
    country_to_users_with_leaning['UK'] = country_to_users_with_leaning['United Kingdom']

    ridge_plot(country_to_uid_leaning_1, 0)
    ridge_plot(country_to_uid_leaning_2, 1)
    ridge_plot(country_to_uid_leaning_3, 2)
    ridge_plot(country_to_uid_leaning_4, 3)