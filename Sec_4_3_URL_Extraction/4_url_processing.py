'''
Merge previously extracted URLs across periods into one file for each country, along with replacing shortened URLs.

Input data:
    Data/Sec_4_3_URL_Extraction/Shortened URL Domains - Cleaned Version.csv
    Data/Sec_4_3_URL_Extraction/URLs/{start_date}_{end_date}/{country}.csv 
        output by `1_url_extraction.py`
    Data/Sec_4_3_URL_Extraction/URLs/urls_redirected.pickle
        output by `3_url_redirection.py`

Output:
    Data/Sec_4_3_URL_Extraction/URLs/processed/{country}.csv

Usage:
    `python Sec_4_3_URL_Extraction/4_url_processing.py`
    
'''


############ replace the path below ############

retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'
url_path = 'Data/Sec_4_3_URL_Extraction/URLs/'

retweet_net_path = '/Users/caiyang/Documents/_Honours/results/Geoparsed_results/User_Retweet_with_Politician/'
url_path = '/Users/caiyang/Documents/_Honours/results/Geoparsed_results/URLs/'
url_path_savepath = 'Data/Sec_4_3_URL_Extraction/URLs/'

############ replace the path above ############

import pickle
import pandas as pd
import os
import up

from utils.config import ALL_DATES, SELECTED_COUNTRIES
from utils.url import reconstruct_url


path = 'Data/Sec_4_3_URL_Extraction/Shortened URL Domains - Cleaned Version.csv'
df = pd.read_csv(path)

df_ = df[df['Resolved Domain'].notnull()]
domain_resolved = dict(zip( df_.Domain, df_['Resolved Domain']   ))
domain_unresolved = df[df['Resolved Domain'].isnull()].Domain.values

savepath = f'{url_path}/urls_redirected.pickle'

with open(savepath, "rb") as f:
    urls_redirected = pickle.load(f)

urls_redirected = {url: url_redirected for url, url_redirected in urls_redirected.items() if url_redirected != ''}
urls_redirected_rescons = {  url: reconstruct_url(redirect) for url, redirect in urls_redirected.items()  }

for idx, country in enumerate(SELECTED_COUNTRIES):
    
    df_merged = None
    
    filepath = f"{retweet_net_path}/Country_Network/{country}/"

    with open(f"{filepath}/lp_prediction/uid_to_leaning_lp.pickle", 'rb') as handle:
        uid_to_leaning = pickle.load(handle)
    
    for month in range(len(ALL_DATES)):

        periods = ALL_DATES[month]
        start_date = periods[0]
        end_date = periods[-1]

        selected_period = f"urls_{start_date}_to_{end_date}"

        filepath = f"{url_path}/{selected_period}/{country}.csv"
        
        columns = ['tweet_id', 'uid', 'name', 'location', 'link']
        
        if df_merged is None:
            df_merged = pd.read_csv(filepath, header=None, names=columns, low_memory=False)
            df_merged = df_merged[df_merged.uid.astype(str).isin(uid_to_leaning)]
        else:
            df_new = pd.read_csv(filepath, header=None, names=columns, low_memory=False)
            df_new = df_new[df_new.uid.astype(str).isin(uid_to_leaning)]
            df_merged = df_merged.append(df_new, ignore_index=True)
            del df_new

    
    links = df_merged.link
    links_recons = [ reconstruct_url(l) for l in links ]
        
    links_new = [ ]
    links_recons_new = [ ]

    for idx, original_link in enumerate(links):
        if original_link in urls_redirected:
            links_new.append( urls_redirected[original_link] )
            link_recons_ = urls_redirected_rescons[original_link]

            links_recons_new.append( link_recons_ )
        else:
            links_new.append( original_link )
            link_recons_ = links_recons[idx]
            if link_recons_ in domain_resolved:
                link_recons_ = domain_resolved[link_recons_]

            links_recons_new.append(link_recons_)
    
    df_merged['link'] = links_new
    df_merged['links_recons'] = links_recons_new
    
    df_merged = df_merged[~df_merged.links_recons.isin(domain_unresolved)]
                    
    if not os.path.exists(f'{url_path_savepath}/processed/'):
        os.makedirs(f'{url_path_savepath}/processed/')
                    
    savepath = f'{url_path_savepath}/processed/{country}.csv'
    df_merged.to_csv(savepath, index=False)
    
    del df_merged
    