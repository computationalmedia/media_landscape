'''
Save seed users in the eight selected country before label spreading

Input data:
    Data/Sec_4_1_Geolocation/Politicians/*
    Data/Sec_4_2_Label_Spreading/Country-specific stats - Party to Leaning.csv
    
Output:
    Data/Sec_4_2_Label_Spreading/Politician_List/country_to_id_leaning.pickle
        seed user and their leaning in each country
    Data/Sec_4_2_Label_Spreading/Politician_Collection/
        this folder contains what we promised to release in the paper
    
Usage:
    `python Sec_4_2_Label_Spreading/1_country_to_seed_users.py`
'''

############ replace the path below ############

seed_user_savepath = "Data/Sec_4_2_Label_Spreading/Politician_List/"
politician_collection_savepath = 'Data/Sec_4_2_Label_Spreading/Politician_Collection/'

############ replace the path above ############


import os
import pickle
import pandas as pd
import up

from utils.config import SELECTED_COUNTRIES

# France
party = 'Libertés and Territories Group'
party = 'Group Centrist Union'

# Spain
party = 'Grupo Parlamentario Plural'
party = 'Mixed Parliamentary Group'

party = 'Libertés and Territories Group'

FR_LTG = \
{'Centrist Alliance': 'C',
 'Independent Republicans': 'R',
 'La République En Marche': 'C',
 'Liberté Écologie Fraternité': '?',
 'Place publique': 'L',
 'Pè a Corsica': '?',
 'Radical Movement': 'C',
 'Radical Party of the Left': 'L',
 'Résistons!':'R' ,
 'Socialist Party': 'L',
 'The New Democrats': 'L',
 'Union for French Democracy': 'R',
 'Union for a Popular Movement': 'R',
 'Union of Democrats and Independents': 'R',
 'miscellaneous left': 'L'
}

FR_LTG = {k.lower(): v for k, v in FR_LTG.items()}


party = 'Group Centrist Union'

FR_GCU = \
{'Centrist Alliance': 'C',
 'Democratic European Force': 'R',
 'Democratic Movement': 'R',
 'Social Democratic Party': 'C',
 "Tahoera'a Huiraatira": 'R',
 'Union for French Democracy': 'R',
 'Union of Democrats and Independents': 'R',
}

FR_GCU = {k.lower(): v for k, v in FR_GCU.items()}


party = 'Grupo Parlamentario Plural'

ES_GPP = \
{'Ahora Madrid': 'L',
 'Canarian Coalition': 'R',
 'Catalan European Democratic Party': 'R',
 'Centrem': 'R',
 'Compromís': 'L',
 'Democratic Convergence of Catalonia': 'R',
 'Galician Nationalist Bloc': 'L',
 "Galician People's Union": 'L',
 'Junts per Catalunya': 'R',
 'Más País': 'L',
 'New Canaries': 'L',
 'Partit per la Independència': 'R',
 'Podemos': 'L',
 'Regionalist Party of Cantabria': 'L',
 'Socialist Action Party': 'L',
 'United Left': 'L',
 'Valencian Nationalist Bloc': 'L',
 'Verdes Equo': 'L',
}

ES_GPP = {k.lower(): v for k, v in ES_GPP.items()}


party = 'Mixed Parliamentary Group'

ES_mixed_par = \
{
    '2978274629': 'L',
    '312297259': 'L',
    '402593346': 'L',
    '3108277737': 'R',
    '144600462': 'R'
}

ES_MPG = \
{'Amaiur': 'L',
 'Aralar Party': 'L',
 'Asturias Forum': 'C',
 'Euskal Herria Bildu': 'L',
 "Navarrese People's Union": 'R',
 "People's Party": 'R',
 'Poble Lliure': 'L',
 'Popular Unity Candidacy': 'L'
}


ES_MPG = {k.lower(): v for k, v in ES_MPG.items()}


selected_countries_iso2 = ['US', 'UK', 'CA', 'AU', 'FR', 'DE', 'ES', 'TR']
iso2_to_country = dict(zip(selected_countries_iso2, SELECTED_COUNTRIES))


path = 'Data/Sec_4_2_Label_Spreading/Country-specific stats - Party to Leaning.csv'
df = pd.read_csv(path)

country_to_party_leaning = {c: {} for c in SELECTED_COUNTRIES}

for idx, row in df.iterrows():
    iso2, party, leaning = row.Country, row.Party, row['collapse to three-point scale'] 
    if iso2 not in iso2_to_country:
        continue
    country = iso2_to_country[iso2]    
    
    if party == 'Socialist Radical Citizen and Miscellaneous Left':
        party_ = 'Socialist, Radical, Citizen and Miscellaneous Left'
        country_to_party_leaning[country][party_.lower()] = leaning
    elif country == 'Australia' and party.lower() == 'coalition':
        country_to_party_leaning[country]['liberal party of australia'] = leaning
        country_to_party_leaning[country]['national party of australia'] = leaning
        
    country_to_party_leaning[country][party.lower()] = leaning
    
    
country_to_party_leaning['France'].update(FR_LTG)
country_to_party_leaning['France'].update(FR_GCU)
country_to_party_leaning['Spain'].update(ES_GPP)
country_to_party_leaning['Spain'].update(ES_MPG)


country_to_politician_id = {c: [] for c in selected_countries_iso2}
country_to_id_leaning = {}
country_to_politicians = {}
country_politician_collection = {}
label_to_avoid = {'?', 'Unknown', 'Big Tent', }



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
        
for country in selected_countries_iso2:

    file_list = country_to_file[country]
    country_pol_id_leaning = {}
    country_politicians = set()
    country_pol_coll = []
    
    country_party = country_to_party_leaning[iso2_to_country[country]]
    
    for file in file_list:
        df = pd.read_csv(file)
        if df.shape[0] == 0:
            continue
        
        for idx, row in df.iterrows():
            name, tid, group, groupFromState, wiki = row['name'], row.twitterID, row.group, row.groupFromState, row.wikidataID
            
            if pd.isnull(group) and pd.isnull(groupFromState):
                continue
            elif pd.isnull(groupFromState) or ( groupFromState.startswith('Q') and not pd.isnull(group)):
                party = group
            else:
                party = groupFromState
                
            
            if not pd.isnull(groupFromState) and \
                groupFromState in ['Libertés and Territories Group', 'Group Centrist Union', 
                                   'Grupo Parlamentario Plural', 'Mixed Parliamentary Group']:
                
                if pd.isnull(group):
                    continue
                party = group
            
            party = party.lower()
            
            if 'independent politician' in party:
                continue
            
            party = party.split("||")
            party = [i.strip() for i in party]
                        
            
            leaning_set = []
            for p in party:
                if p not in country_party:
                    leaning_set.append('Unknown')
                    continue
                
                if country_party[p] == 'C':
                    continue
                    
                leaning_set.append( country_party[p] )
                
            leaning_set = set(leaning_set)
            
            if len(label_to_avoid&leaning_set) > 0:
                continue
            
            if not leaning_set:
                continue
            elif 'L' in leaning_set and 'R' in leaning_set:
                continue
            
            country_politicians.add(name.lower())
            
            leaning = leaning_set.pop()
            
            tids = str(tid).split("||")
            tids = [i.strip() for i in tids]
            
            for tid in tids:
                country_pol_id_leaning[tid] = leaning
                
            country_pol_coll.append( [ country, name.lower(), party, leaning, tids, wiki ] )
            
    country_to_id_leaning[iso2_to_country[country]] = country_pol_id_leaning
    country_to_politicians[iso2_to_country[country]] = country_politicians
    country_politician_collection[iso2_to_country[country]] = country_pol_coll
    

DE_update = {
    'alliance 90/the greens': 'L',
    'free democratic party': 'R',
    'christian social union of bavaria': 'R' 
}

FR_update = {
    'corsica libera': 'L',
    'united guadeloupe solidary and responsible': 'C',
    'soyons libres': 'R',
    'martinican democratic rally': 'L'
}

ES_update = {
    'together for catalonia': 'R'
}

UK_update = {
    'welsh labour': 'L',
    'progressive labour party': 'L',
    'virgin islands party': '?',
    "people's progressive movement": 'L',
    'gibraltar socialist labour party': 'L',
    "people's democratic movement": 'R'
}

country_to_party_leaning['Germany'].update(DE_update)
country_to_party_leaning['France'].update(FR_update)
country_to_party_leaning['Spain'].update(ES_update)
country_to_party_leaning['United Kingdom'].update(UK_update)


# elections
election_path = "Data/Sec_4_1_Geolocation/Politicians/Elections"
election_id_to_party = {}
election_names = {}
election_politician_collection = {}

for file in os.listdir(election_path):
    if not file.endswith('txt'):
        continue
    
    file_path = os.path.join(election_path, file)
    country = iso2_to_country[ file.split("_")[0] ]
    print(country)
    country_elec_id_to_party = {}
    country_cands = set()
    country_pol_coll = []
    
    with open(file_path, "r") as f:
        lines = f.readlines()
        
    for line in lines:
        line_split = line.split(",")
        line_split = [i.strip() for i in line_split]
        if line_split[-1] == '?': # unknown twitter handles
            continue
        
        raw_leaning = line_split[2].lower()
        if 'left' in raw_leaning:
            leaning = 'L'
        elif 'right' in raw_leaning:
            leaning = 'R'
        else:
            continue
        
        country_cands.add(line_split[0].lower())
        
        twitter_ids = [i for i in line_split[3:]]
        for tid in twitter_ids:
            country_elec_id_to_party[tid] = leaning
        
        country_pol_coll.append( [ country, line_split[0].lower(), [ line_split[1].lower() ], 
                                  leaning, twitter_ids ] )
              
    election_id_to_party[country] = country_elec_id_to_party
    election_names[country] = country_cands
    election_politician_collection[country] = country_pol_coll
    
    
governor_path = 'Data/Sec_4_1_Geolocation/Politicians/Governors_supp'
governor_id_to_party = {}
governor_names = {}
governor_politician_collection = {}

for file in os.listdir(governor_path):
    if not file.endswith('txt'):
        continue
    
    file_path = os.path.join(governor_path, file)
    country = file.split(".")[0]
    print(country)
    
    country_party = country_to_party_leaning[country]
    country_govern_id_to_party = {}
    country_cands = set()
    country_pol_coll = []
    
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    counter = 0
    for line in lines:
        line_split = line.split(",")
        line_split = [i.strip() for i in line_split]
        party_name = line_split[1].lower()
        
        if line_split[-1] == '?' or party_name == '?' or 'independent' in party_name: # unknown twitter handles
            continue
        
        if country == 'Argentina':
            twitter_ids = [i for i in line_split[3:]]
        else:
            twitter_ids = [i for i in line_split[2:]]
        
        if party_name not in country_party:
            print(f"{country}: {party_name}")
            continue
            
        mapped_leaning = country_party[party_name]
        if mapped_leaning != 'L' and mapped_leaning != 'R':
            continue
        
        country_cands.add(line_split[0].lower())
        
        for tid in twitter_ids:
            country_govern_id_to_party[tid] = mapped_leaning
            
        country_pol_coll.append( [ country, line_split[0].lower(), [ line_split[1].lower() ], 
                                  mapped_leaning, twitter_ids ] )
              
                    
    governor_id_to_party[country] = country_govern_id_to_party
    governor_names[country] = country_cands
    governor_politician_collection[country] = country_pol_coll
    
    
for country, id_to_party in election_id_to_party.items():
    country_to_id_leaning[country].update(id_to_party)
    
for country, id_to_party in governor_id_to_party.items():
    country_to_id_leaning[country].update(id_to_party)

if not os.path.isdir(seed_user_savepath):
    os.makedirs(seed_user_savepath)
with open(f"{seed_user_savepath}/country_to_id_leaning.pickle", "wb") as f:
    pickle.dump(country_to_id_leaning, f)
    
    
    
# the following output saves politicians' information
# they're already in Data/Sec_4_2_Label_Spreading/Politician_Collection/
for country, pol_names in election_politician_collection.items():
    country_politician_collection[country] += pol_names

for country, pol_names in governor_politician_collection.items():
    country_politician_collection[country] += pol_names
    
if not os.path.isdir(politician_collection_savepath):
    os.makedirs(politician_collection_savepath)

for country in SELECTED_COUNTRIES:
        
    pol_collection = country_politician_collection[country]
    
    with open(f"{politician_collection_savepath}/{country}.txt", "w") as f:
        for info in pol_collection:
            line_to_write = []
            for element in info[1:]:
                if type(element) is list:
                    line_to_write.append( "; ".join(element) )
                else:
                    line_to_write.append(element)
            line_to_write = '\t'.join(line_to_write) + "\n"
            f.writelines(line_to_write)
            