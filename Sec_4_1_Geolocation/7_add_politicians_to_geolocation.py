'''
Add politicians' Twitter IDs and their countries to existing geolocation.

Input data:
    Data/Sec_4_1_Geolocation/geoparse/merged_uid_to_world_loc.pickle
        output by `6_merge_geotag_geoparse.py`
    Data/Sec_4_1_Geolocation/Politicians/*
    
Output:
    Data/Sec_4_1_Geolocation/geoparse/merged_uid_to_world_loc_w_pol.pickle
    
Usage:
    `python Sec_4_1_Geolocation/7_add_politicians_to_geolocation.py`
'''

############ replace the path below ############

uid_to_loc_path = 'Data/Sec_4_1_Geolocation/geoparse/'
merged_uid_to_loc_savepath = 'Data/Sec_4_1_Geolocation/geoparse/'

############ replace the path above ############


import os
import pickle
import pandas as pd


path = 'Data/Sec_4_1_Geolocation/Politicians/Legislators_Results'

country_to_file = {}

for file in os.listdir(path):
    if not file.endswith('csv'):
        continue
    country = file.split("_")[0]
    if country not in country_to_file:
        country_to_file[country] = [ os.path.join(path, file) ]
    else:
        country_to_file[country] += [ os.path.join(path, file) ]
        
        
path = f"{uid_to_loc_path}/merged_uid_to_world_loc.pickle"
with open(path, "rb") as f:
    users_to_unq_loc = pickle.load(f)
    

selected_countries = ['United States', 'United Kingdom', 'Canada', 'Australia', 'France', 'Germany', 'Spain', 'Turkey', ]

selected_countries_iso2 = ['US', 'UK', 'CA', 'AU', 'FR', 'DE', 'ES', 'TR']

iso2_to_country = dict(zip(selected_countries_iso2, selected_countries))


# legislators
for idx, iso2 in enumerate( selected_countries_iso2 ):
    
    country = selected_countries[idx]
    file_list = country_to_file[iso2]
    country_uids = []
    
    for file in file_list:
        df = pd.read_csv(file)
        if df.shape[0] == 0:
            continue
        
        uids = df.twitterID.astype("string").values
        for uid in uids:
            uid_ = uid.split("||")
            uid_ = [i.strip() for i in uid_]
            country_uids += uid_
            
    for uid in country_uids:
        users_to_unq_loc[uid] = country



# elections
election_path = "Data/Sec_4_1_Geolocation/Politicians/Elections"
election_id_to_loc = {}

for file in os.listdir(election_path):
    if not file.endswith('txt'):
        continue
    
    file_path = os.path.join(election_path, file)
    country = iso2_to_country[ file.split("_")[0] ]
    
    with open(file_path, "r") as f:
        lines = f.readlines()
        
    for line in lines:
        line_split = line.split(",")
        line_split = [i.strip() for i in line_split]
        if line_split[-1] == '?': # unknown twitter handles
            continue
        
        twitter_ids = [i for i in line_split[3:]]
        for tid in twitter_ids:
            election_id_to_loc[tid] = country


# governors
governor_path = "Data/Sec_4_1_Geolocation/Politicians/Governors_supp"
governor_id_to_loc = {}

for file in os.listdir(governor_path):
    if not file.endswith('txt'):
        continue
    
    file_path = os.path.join(governor_path, file)
    
    country = file.split(".")[0]
    
    with open(file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        line_split = line.split(",")
        line_split = [i.strip() for i in line_split]
        if line_split[-1] == '?': # unknown twitter handles
            continue
        if country != 'Argentina':
            twitter_ids = [i for i in line_split[2:]]
        else:
            twitter_ids = [i for i in line_split[3:]]
        for tid in twitter_ids:
            governor_id_to_loc[tid] = country


for tid, country in election_id_to_loc.items():
    users_to_unq_loc[tid] = country
    
for tid, country in governor_id_to_loc.items():
    users_to_unq_loc[tid] = country    

with open(f"{merged_uid_to_loc_savepath}/merged_uid_to_world_loc_w_pol.pickle", "wb") as f:
    pickle.dump(users_to_unq_loc, f)