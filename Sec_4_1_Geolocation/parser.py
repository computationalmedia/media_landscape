import os
import pandas as pd
import re
import emoji
import json 
from nltk.corpus import stopwords


def remove_emoji(text):
    return emoji.get_emoji_regexp().sub(u'', text)


class Parser():
    def __init__(self):       
        pass 

    def load_data(self, data_dir='data'):

        path = os.path.join(data_dir, 'stateName_to_stateAbbrv.json')
        with open(path, "r") as f:
            us_state_name_to_abbrev = json.load(f)

        world_city_df = pd.read_csv(os.path.join(data_dir, 'worldcities.csv'))
        world_city_pd = world_city_df[ ( world_city_df.admin_name.notnull() ) & ( world_city_df.iso2.notnull() ) ]

        old_columns = list(world_city_pd.columns)

        world_city_pd.loc[:, 'city_ascii_lower'] = world_city_pd.apply(lambda x: x.city_ascii.lower(), axis=1)
        world_city_pd.loc[:, 'admin_name_lower'] = world_city_pd.apply(lambda x: x.admin_name.lower(), axis=1)
        world_city_pd.loc[:, 'admin_abbrev_lower'] = world_city_pd.apply(lambda x: us_state_name_to_abbrev[x.admin_name_lower].lower() if x.admin_name_lower in us_state_name_to_abbrev else None, axis=1)
        world_city_pd.loc[:, 'country_lower'] = world_city_pd.apply(lambda x: x.country.lower(), axis=1)

        world_city_pd.loc[:,'city_admin'] = world_city_pd.apply(lambda x: x.city_ascii.lower()+' '+x.admin_name.lower(), axis=1)
        world_city_pd.loc[:,'admin_city'] = world_city_pd.apply(lambda x: x.admin_name.lower()+' '+x.city_ascii.lower(), axis=1)
        world_city_pd.loc[:,'city_admin_abbrev'] = world_city_pd.apply(lambda x: x.city_ascii.lower()+' '+x.admin_abbrev_lower.lower() if type(x.admin_abbrev_lower) is str else None, axis=1)
        world_city_pd.loc[:,'admin_abbrev_city'] = world_city_pd.apply(lambda x: x.city_ascii.lower()+' '+x.admin_abbrev_lower.lower() if type(x.admin_abbrev_lower) is str else None, axis=1)

        world_city_pd.loc[:,'admin_country'] = world_city_pd.apply(lambda x: x.admin_name.lower()+' '+x.country.lower(), axis=1)
        world_city_pd.loc[:,'admin_iso2'] = world_city_pd.apply(lambda x: x.admin_name.lower()+' '+x.iso2.lower(), axis=1)
        world_city_pd.loc[:,'admin_iso3'] = world_city_pd.apply(lambda x: x.admin_name.lower()+' '+x.iso3.lower(), axis=1)
        world_city_pd.loc[:,'admin_abbrev_iso2'] = world_city_pd.apply(lambda x: x.admin_abbrev_lower.lower()+' '+x.iso2.lower() if type(x.admin_abbrev_lower) is str else None, axis=1)
        world_city_pd.loc[:,'admin_abbrev_iso3'] = world_city_pd.apply(lambda x: x.admin_abbrev_lower.lower()+' '+x.iso3.lower() if type(x.admin_abbrev_lower) is str else None, axis=1)

        world_city_pd.loc[:,'country_admin'] = world_city_pd.apply(lambda x: x.country.lower()+' '+x.admin_name.lower(), axis=1)
        world_city_pd.loc[:,'iso2_admin'] = world_city_pd.apply(lambda x: x.iso2.lower()+' '+x.admin_name.lower(), axis=1)
        world_city_pd.loc[:,'iso3_admin'] = world_city_pd.apply(lambda x: x.iso3.lower()+' '+x.admin_name.lower(), axis=1)
        world_city_pd.loc[:,'iso2_admin_abbrev'] = world_city_pd.apply(lambda x: x.iso2.lower()+' '+x.admin_abbrev_lower.lower() if type(x.admin_abbrev_lower) is str else None, axis=1)
        world_city_pd.loc[:,'iso3_admin_abbrev'] = world_city_pd.apply(lambda x: x.iso3.lower()+' '+x.admin_abbrev_lower.lower() if type(x.admin_abbrev_lower) is str else None, axis=1)

        world_city_pd.loc[:,'city_country'] = world_city_pd.apply(lambda x: x.city_ascii.lower() +' '+x.country.lower(), axis=1)
        world_city_pd.loc[:,'city_iso2'] = world_city_pd.apply(lambda x: x.city_ascii.lower() +' '+x.iso2.lower(), axis=1)
        world_city_pd.loc[:,'city_iso3'] = world_city_pd.apply(lambda x: x.city_ascii.lower() +' '+x.iso3.lower(), axis=1)

        world_city_pd.loc[:,'country_city'] = world_city_pd.apply(lambda x: x.country.lower() +' '+x.city_ascii.lower(), axis=1)
        world_city_pd.loc[:,'iso2_city'] = world_city_pd.apply(lambda x: x.iso2.lower() +' '+x.city_ascii.lower(), axis=1)
        world_city_pd.loc[:,'iso3_city'] = world_city_pd.apply(lambda x: x.iso3.lower() +' '+x.city_ascii.lower(), axis=1)

        world_city_pd.loc[:,'county_state_city'] = world_city_pd.apply(lambda x:x.country.lower()+' '+x.admin_name.lower()+' '+x.city_ascii.lower(), axis=1)
        world_city_pd.loc[:,'iso2_state_city'] = world_city_pd.apply(lambda x:x.iso2.lower()+' '+x.admin_name.lower()+' '+x.city_ascii.lower(), axis=1)
        world_city_pd.loc[:,'iso3_state_city'] = world_city_pd.apply(lambda x:x.iso3.lower()+' '+x.admin_name.lower()+' '+x.city_ascii.lower(), axis=1)

        world_city_pd.loc[:,'city_state_country'] = world_city_pd.apply(lambda x:x.city_ascii.lower()+' '+x.admin_name.lower()+' '+x.country.lower(), axis=1)
        world_city_pd.loc[:,'city_state_iso2'] = world_city_pd.apply(lambda x:x.city_ascii.lower()+' '+x.admin_name.lower()+' '+x.iso2.lower(), axis=1)
        world_city_pd.loc[:,'city_state_iso3'] = world_city_pd.apply(lambda x:x.city_ascii.lower()+' '+x.admin_name.lower()+' '+x.iso3.lower(), axis=1)

        new_columns = list(world_city_pd.columns)
        new_columns.remove('admin_abbrev_lower')

        self.mappings_keys = [col for col in new_columns if col not in old_columns]
        self.world_city_pd = world_city_pd

        languages = ['dutch', 'english', 'french', 'german', 'italian', 'portuguese', 'russian', 'spanish', 'swedish']

        stopwords_to_removed = []

        for lang in languages:
            
            lang_stop = stopwords.words(lang)
            stopwords_to_removed += list(lang_stop)

        self.stopwords_to_removed = stopwords_to_removed

    def create_n_grams(self, text, n):
        text_list = text.split()
        return [ " ".join(text_list[i:i+n]) for i in range(0, len(text_list) - n + 1) ]


    def parse_location(self, text):
        text = remove_emoji(text)
        
        if text is None or len(text) == 0:
            return set(), set()
        
        possible_countries = set()
        corresponding_admins = set()

        # quick check on location by replacing 
        location_ = text.replace("\n", " ").replace('，', ' ').replace('—', ' ').replace(',', ' ').replace(';', ' ').replace('/', ' ').replace('.', ' ').strip()
        location_ = re.sub(' +',' ',location_)
        
        if 'dc' in location_.split(' '):
            location_ = location_.replace('dc', 'district of columbia')
            
        elif 'd.c.' in location_.split(' '):
            location_ = location_.replace('d.c.', 'district of columbia')
        
        if 'america' in location_.split(' '):
            location_ = location_.replace('america', 'united states')
            
        if 'uk'  in location_.split(' '): # uk is not in record
            location_ = location_.replace('uk', 'united kingdom')
        
        location_ = location_.split()
        location_ = [ i for i in location_ if i not in self.stopwords_to_removed ]
        location_ = " ".join(location_)

        location_n_grams_all = [ [location_] ] + [ self.create_n_grams(location_, n) for n in range(len(location_.split())-1, 0, -1) ]

        for location_ngrams in location_n_grams_all:
        
            for loc_ngram in location_ngrams:

                for mapping_idx, mapping_key in enumerate(self.mappings_keys):

                    res_df =self.world_city_pd[self.world_city_pd[mapping_key] == loc_ngram]

                    res = set( res_df.country.unique() )

                    possible_countries |= res

                    if 'United States' in res and mapping_key != 'country_lower':

                        admins = set( res_df[res_df.country == 'United States'].admin_name.unique() )

                        corresponding_admins |= admins

            if len(possible_countries) > 0:
                break
            
        return possible_countries, corresponding_admins
        