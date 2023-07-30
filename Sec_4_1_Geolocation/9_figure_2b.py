'''
Figure 2b in the paper

Input data:
    Data/Sec_4_1_Geolocation/lang_stats/lang_stats_{start_date}_{end_date}.pickle
        output by `8_lang_stats.py`
        
Output:
    Plots/top2_languages_top20_countries.pdf
        figure 2b in the paper
        
Example usage:
    `python Sec_4_1_Geolocation/9_figure_2b.py`
    
'''

############ replace the path below ############

lang_stats_path = 'Data/Sec_4_1_Geolocation/lang_stats/'
figure_savepath = "Plots/"

############ replace the path above ############


import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import up

from collections import defaultdict

from utils.config import ALL_DATES, SELECTED_COUNTRIES

country_to_languages = defaultdict(dict)

for idx in range(len(ALL_DATES)) :

    periods = ALL_DATES[idx]
    start_date = periods[0]
    end_date = periods[-1]
    
    filepath = f"{lang_stats_path}/lang_stats_{start_date}_{end_date}.pickle"

    with open(filepath, "rb") as f:
        date_to_country_lang = pickle.load(f)
    
    
    for country_to_lang in date_to_country_lang.values():
        for country, country_lang in country_to_lang.items():
            for lang, lang_cnt in country_lang.items():
                if lang not in country_to_languages[country]:
                    country_to_languages[country][lang] = lang_cnt
                else:
                    country_to_languages[country][lang] += lang_cnt
         
    
    
country_top3_lang = dict()

for country, country_lang in country_to_languages.items():
    lang_counter = sorted(country_lang.items(), key=lambda x: x[1])[::-1]
    total_cnt = sum([i[1] for i in lang_counter])
    lang_counter = lang_counter[:2]
    
    lang_counter = [ (i[0], i[1]/total_cnt) for i in lang_counter]
    
    country_top3_lang[country] = lang_counter
    
first_lang_ratio = []
first_lang = []
second_lang_ratio = []
second_lang = []

country_list = ['United States', 'India', 'United Kingdom', 'Indonesia', 'Brazil', 'Turkey', 'France', 'Canada', 'Argentina', 
 'Mexico', 'Nigeria', 'Philippines', 'Spain', 'South Africa', 'Malaysia', 'Australia', 'Colombia', 'Pakistan',
 'Venezuela', 'Germany'] # top 20 countries

for country in country_list:
    lang_used = country_top3_lang[country]
    first_lang.append( lang_used[0][0] )
    first_lang_ratio.append( lang_used[0][1] )
    second_lang.append( lang_used[1][0] )
    second_lang_ratio.append( lang_used[1][1] )
    
all_langs = list( set(first_lang) | set(second_lang) )
all_langs = ['en', 'und', 'es', 'de', 'pt', 'hi', 'ur', 'tr', 'tl', 'fr', 'in']
lang_to_color = { lang: sns.color_palette('Paired')[idx] for idx, lang in enumerate(all_langs) }

fig = plt.figure(figsize=(15, 5), dpi=300)

ax = fig.add_subplot(111)

df_dict = {'country': country_list, 'first': first_lang_ratio, 'second': second_lang_ratio}

df = pd.DataFrame(df_dict)
df.set_index('country', inplace=True)

df.plot.bar(stacked=True, ax=ax, rot=0, color='c', legend=[], width=0.75)

for idx, p in enumerate( ax.patches ):
    lang = (first_lang + second_lang)[idx]
    bar_color = lang_to_color[lang]
    p.set_facecolor(bar_color)
    
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

    
_ = plt.xticks(rotation=90, fontsize=24)

plt.tick_params(axis='both', which='major', labelsize=22)

plt.ylabel('Ratio of Top 2 Languages  ', fontsize=24)

labels = list(lang_to_color.keys())
handles = [plt.Rectangle((0,0),1,1, color=lang_to_color[label]) for label in labels]
plt.legend(handles, labels, bbox_to_anchor=(1.0, 1.0), facecolor=(1.0,1.0,1.0,1.0), 
           frameon=False, prop={'size': 20})

for idx, cty in enumerate(country_list):
    if cty in SELECTED_COUNTRIES:
        ax.get_xticklabels()[idx].set_weight("bold")

plt.xlabel("")
plt.grid(False)

fig_savepth = f"{figure_savepath}/top2_languages_top20_countries.pdf"
fig.savefig(fig_savepth, bbox_inches='tight', facecolor=(1.0,1.0,1.0,1.0), dpi=100)