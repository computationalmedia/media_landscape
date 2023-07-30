'''
Merge geotagging and geoparsing results

Input data:
    Data/Sec_4_1_Geolocation/geotag/users_to_unq_loc.pickle
        output by `2_geotag_process.py`
    Data/Sec_4_1_Geolocation/geoparse/uid_to_world_loc.pickle
        output by `5_map_uid_to_loc.py`
    
Output:
    Data/Sec_4_1_Geolocation/geoparse/merged_uid_to_world_loc.pickle
    
Usage: 
    `python Sec_4_1_Geolocation/6_merge_geotag_geoparse.py`
'''

############ replace the path below ############

geotag_user_id_to_loc_path = 'Data/Sec_4_1_Geolocation/geotag/'
geoparse_user_id_to_loc_path = 'Data/Sec_4_1_Geolocation/geoparse/'
merged_user_id_to_loc_savepath = 'Data/Sec_4_1_Geolocation/geoparse/'

############ replace the path above ############


import pickle

with open(f"{geoparse_user_id_to_loc_path}/uid_to_world_loc.pickle", "rb") as f:
    uid_to_world_loc = pickle.load(f)
    
with open(f"{geotag_user_id_to_loc_path}/users_to_unq_loc.pickle", "rb") as f:
    users_to_unq_iso2 = pickle.load(f)
    
geotag_world_users = set(users_to_unq_iso2.keys())
geotag_world_users = {int(i) for i in geotag_world_users}

geoparse_world_users = set(uid_to_world_loc.keys())

world_overlap = list( geotag_world_users&geoparse_world_users )

labels = [ users_to_unq_iso2[str(i)] for i in world_overlap ]
parse_res = [ uid_to_world_loc[i] for i in world_overlap ]

prec_cnt = sum([1 for i in range(len(labels)) if labels[i] == parse_res[i] ])

print("Accuracy", prec_cnt/len(world_overlap))


merged_uid_to_world_loc = {}

for uid, parsed_world_loc in uid_to_world_loc.items():
    if str(uid) in users_to_unq_iso2:
        merged_uid_to_world_loc[str(uid)] = users_to_unq_iso2[str(uid)]
    else:
        merged_uid_to_world_loc[str(uid)] = parsed_world_loc

with open(f"{merged_user_id_to_loc_savepath}/merged_uid_to_world_loc.pickle", "wb") as f:
    pickle.dump(merged_uid_to_world_loc, f)
    