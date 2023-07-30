'''
Further process extracted geotags from tweets.

Input data:
    Data/Sec_4_1_Geolocation/geotags/users_geotag_{start_date}_{end_date}.pickle on 16 periods
        output by `1_geotag_extraction.py`
    Data/Sec_4_1_Geolocation/countries_codes_and_coordinates.csv
        reference https://gist.github.com/tadast/8827699
    
Output: 
    Data/Sec_4_1_Geolocation/geotags/users_to_unq_loc.pickle
        it contains user id to country ISO2 code

Usage:
    `python Sec_4_1_Geolocation/2_geotag_process.py`
'''

############ replace the path below ############

geotag_path = 'Data/Sec_4_1_Geolocation/geotags/'
save_path = 'Data/Sec_4_1_Geolocation/geotags/'

############ replace the path above ############

import pickle
import pandas as pd
import up

from collections import defaultdict

from utils.config import ALL_DATES

all_users_geotags = defaultdict(set)

for idx in range(len(ALL_DATES)):

    periods = ALL_DATES[idx]
    start_date = periods[0]
    end_date = periods[-1]

    filepath = f"{geotag_path}/users_geotag_{start_date}_{end_date}.pickle"
    
    with open(filepath, "rb") as f:
        users_geotags = pickle.load(f)
    
    for user, places in users_geotags.items():
        all_users_geotags[user] |= places
        
    
df = pd.read_csv('Data/Sec_4_1_Geolocation/countries_codes_and_coordinates.csv')

df['Alpha-2 code'] = df['Alpha-2 code'].apply(lambda x: eval(x))
iso2_to_country = dict( zip( df['Alpha-2 code'], df['Country'] ) )

additional_codes = {
    'AX': 'Åland Islands',
    'BL': 'Saint Barthélemy',
    'BQ': 'Bonaire, Sint Eustatius and Saba',
    'CW': 'Curaçao',
    'MF': 'Saint Martin (French part)',
    'SX': 'Sint Maarten (Dutch part)',
    'XK': 'Kosovo',
}

iso2_to_country.update(additional_codes)


users_to_iso2 = defaultdict(set)

for users, geotags in all_users_geotags.items():
    iso2 = set( [ place[-2] for place in geotags ] )
    users_to_iso2[users] = iso2
    
# get users and their country codes who only have unique conutry code
users_to_unq_iso2 = { user: iso2_to_country[ iso2.pop() ] for user, iso2 in users_to_iso2.items() if len( iso2 ) == 1 and '' not in iso2}

with open(f"{save_path}/users_to_unq_loc.pickle", "wb") as f:
    pickle.dump( users_to_unq_iso2, f)
    