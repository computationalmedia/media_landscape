'''
Map twitter users' ids to their parsed location

Input data:
    Data/Sec_4_1_Geolocation/geoparse/unique_loc_parsed_country.pickle
        output by `4_geoparse.py`
        
Output:
    Data/Sec_4_1_Geolocation/geoparse/user_locations_multi_period_parsed.csv
    Data/Sec_4_1_Geolocation/geoparse/uid_to_world_loc.pickle
    
Usage:
    `python Sec_4_1_Geolocation/5_map_uid_to_loc.py`
'''

############ replace the path below ############

uid_to_world_loc_savepath = 'Data/Sec_4_1_Geolocation/geoparse/'
loc_to_country_path = f'{uid_to_world_loc_savepath}/unique_loc_parsed_country.pickle'
user_multi_period_path = f'{uid_to_world_loc_savepath}/user_locations_multiple_period.csv'
user_multi_period_savepath = f'{uid_to_world_loc_savepath}/user_locations_multi_period_parsed.csv'

############ replace the path above ############


import pickle
import pandas as pd


with open(loc_to_country_path, 'rb') as handle:
    loc_to_country = pickle.load(handle)
    
user_df = pd.read_csv(user_multi_period_path, index_col=0)

locations = user_df.locations

parsed_states = []
parsed_countries = []

for location in locations:
    loc_eval = eval(location)
    
    all_possible_countries = set()
    
    for loc in loc_eval:
        try:
            country = loc_to_country[loc]
            all_possible_countries.add(country)

        except:
            all_possible_countries.add(None)

    if len(all_possible_countries) == 1:
        parsed_countries.append(list(all_possible_countries)[0])
    else:
        parsed_countries.append(None)
        
        
user_df['geo_world'] = parsed_countries
user_df.to_csv(user_multi_period_path, index=False)


user_df = user_df[user_df.geo_world.notnull()]

loc_to_cnt = user_df[['user_id', 'geo_world']].groupby('user_id', as_index=False).nunique()
uids_w_unique_world_loc = loc_to_cnt[loc_to_cnt.geo_world==1].user_id

user_df = user_df[user_df.user_id.isin(uids_w_unique_world_loc)]

uid_to_world_loc = dict(zip(user_df.user_id, user_df.geo_world))

with open(f"{uid_to_world_loc_savepath}/uid_to_world_loc.pickle", "wb") as f:
    pickle.dump(uid_to_world_loc, f)
    