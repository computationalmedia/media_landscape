'''
Figure 2a in the paper

Input data:
    Data/Sec_4_1_Geolocation/geoparse/merged_uid_to_world_loc.pickle
        output by `6_merge_geotag_geoparse.py`
        
Output:
    Plots/number_of_users_20_countries.pdf
        figure 2a in the paper
        
Example usage:
    `python Sec_4_1_Geolocation/9_figure_2a.py`
    
'''

############ replace the path below ############

location_path = 'Data/Sec_4_1_Geolocation/geoparse/'
figure_savepath = 'Plots/'

############ replace the path above ############


import pickle
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import up

from collections import defaultdict, Counter
from utils.config import SELECTED_COUNTRIES

with open(f"{location_path}/merged_uid_to_world_loc_w_pol.pickle", "rb") as f:
    user_to_country = pickle.load(f)
    
country_counter = dict( Counter( user_to_country.values() ).most_common() )
  
country_list = list(country_counter.keys())[:20]

country_counter = {country: country_counter[country] for country in country_list}
total_users = np.log10( np.array( list( country_counter.values() ) ) )



fig = plt.figure(figsize=(15, 5), dpi=300)

ax = fig.add_subplot(111)
plt.grid(axis='y')       

bars = ax.bar(country_list, total_users.tolist(), color='#91BFFF', edgecolor='black')#, label='Users with unique locations')

_ = plt.xticks(rotation=90, fontsize=18)


plt.tick_params(axis='both', which='major', labelsize=22)
plt.ylabel('Number of Geolocated Users', fontsize=24)

_ = plt.yticks(list(range(1, 8, 2)),  [f'10$^{i}$' for i in range(1, 8, 2)])

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

for idx, cty in enumerate(country_list):
    if cty in SELECTED_COUNTRIES:
        ax.get_xticklabels()[idx].set_weight("bold")


plt.grid(False)
plt.xlim(-1, 20)


fig_savepth = f"{figure_savepath}/number_of_users_20_countries.pdf"
fig.savefig(fig_savepth, bbox_inches='tight', facecolor=(1.0,1.0,1.0,1.0), dpi=100)
