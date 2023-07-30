'''
Preprocess dataset from Emily Chen, Kristina Lerman, and Emilio Ferrara. 2020. 
Tracking Social Media Discourse about the COVID-19 Pandemic: Development of a Public Coronavirus Twitter Data Set. JMIR Public Health and Surveillance (2020). 
See repo here: https://github.com/echen102/COVID-19-TweetIDs

This script pre-merge several files together for the convenience of comparison later.


Input data:
    Dataset from Chen et al.
    
Output:
    Merged files of tweet IDs named after dates

Usage: - replace `chen_etal_path` and `savepath` below
    `python Sec_3_COVID2020/1_merge_chen_etal.py`
'''

############ replace the path below ############

chen_etal_path = "Data/Sec_3_COVID2020/COVID-19-TweetIDs/"
savepath = "Data/Sec_3_COVID2020/COVID-19-TweetIDs-merged/"

############ replace the path above ############

import os
import up
from collections import defaultdict
from utils.config import *

if not os.path.exists(savepath):
    os.mkdir(savepath)

# gather files by date 
date_to_files = defaultdict(list)
for period in ALL_DATES:
    
    start_date = period[0]
    end_date = period[-1]

    selected_period = f"{start_date}-{end_date}"
    
    for date in period:
        for folder in os.listdir(chen_etal_path):
            if folder not in YEAR_MONTH:
                continue
        
            for text_file in os.listdir(chen_etal_path+"/"+folder):
                text_file_date = text_file.split('-')
                text_file_date = f"{text_file_date[-3]}-{text_file_date[-2]}"
                if date == text_file_date:
                    date_to_files[date].append(chen_etal_path+"/"+folder+"/"+text_file)
                    
             
# merge files by date
for date, files in date_to_files.items():
    tweet_ids_by_date = None
    for tweet_id_file in files:
        with open(tweet_id_file, "r") as f:            
            if tweet_ids_by_date is None:
                tweet_ids_by_date = f.readlines()
            else:
                tweet_ids_by_date += f.readlines()
                
    tweet_ids_by_date = [i for i in tweet_ids_by_date if i.strip() != ""]
    with open(f"{savepath}/{date}.txt", "w") as f:
        f.writelines(tweet_ids_by_date)
        