'''
Get a list of shortened URLs. You can skip `2_gather_redirected_urls.py` and `3_url_redirection.py` by using our provided processed files.

Input data:
    Data/Sec_4_3_URL_Extraction/Shortened URL Domains - Cleaned Version.csv
        This file was obtained through manual labelling. Domains in this csv file are obtained by intersecting extracted URL domains with
        existing dataset from https://github.com/PeterDaveHello/url-shorteners/blob/master/list 
        along with popular shorteners 'bit.ly', 'dlvr.it', 'trib.al', 'ow.ly', 'buff.ly', 'ift.tt', 'tinyurl', 'is.gd', 'amp.gs', 'flip.it', 'bitly'
        The process was skipped here for simplicity.
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_prediction/uid_to_leaning_lp.pickle
        output by `Sec_4_2_Label_Spreading/8_label_spreading_prediction.py`
        
Output:
    Data/Sec_4_3_URL_Extraction/URLs/urls_to_redirect.pickle

Usage:
    `python Sec_4_3_URL_Extraction/2_gather_redirected_urls.py`
'''

############ replace the path below ############

retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'
url_path = 'Data/Sec_4_3_URL_Extraction/URLs/' # this is also where the file will be saved

retweet_net_path = '/Users/caiyang/Documents/_Honours/results/Geoparsed_results/User_Retweet_with_Politician/'
url_path = '/Users/caiyang/Documents/_Honours/results/Geoparsed_results/URLs/'
url_path_savepath = 'Data/Sec_4_3_URL_Extraction/URLs/'

############ replace the path above ############


import pandas as pd
import pickle
import os
import up
from utils.config import ALL_DATES, SELECTED_COUNTRIES
from utils.url import reconstruct_url


path = 'Data/Sec_4_3_URL_Extraction/Shortened URL Domains - Cleaned Version.csv'
df = pd.read_csv(path)

domains_need_redirect = df[df['Resolved Domain'].isnull()].Domain.values

urls_to_redirect = set()

for idx, country in enumerate(SELECTED_COUNTRIES):
    
    df_merged = None
    
    filepath = f"{retweet_net_path}/Country_Network/{country}/"

    with open(f"{filepath}/lp_prediction/uid_to_leaning_lp.pickle", 'rb') as handle:
        uid_to_leaning = pickle.load(handle)
    
    for month in range(len(ALL_DATES)):

        periods = ALL_DATES[month]
        start_date = periods[0]
        end_date = periods[-1]

        selected_period = f"locations_{start_date}_to_{end_date}"

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

    df_merged['links_recons'] = links_recons

    del links, links_recons
    
    shorten_url_df = df_merged[df_merged.links_recons.isin(domains_need_redirect)]
    country_urls = shorten_url_df.link.values
    
    urls_to_redirect |= set(country_urls)
    

if not os.path.isdir(url_path_savepath):
    os.makedirs(url_path_savepath)
with open(f"{url_path_savepath}/urls_to_redirect.pickle", "wb") as f:
    pickle.dump(list(urls_to_redirect), f)