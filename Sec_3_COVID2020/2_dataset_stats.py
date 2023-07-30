'''
Calculate the stats of the given dataset. It needs to be run on all 16 periods for complete iteration of the dataset.

And compare with existing work: 
    Emily Chen, Kristina Lerman, and Emilio Ferrara. 2020. 
    Tracking Social Media Discourse about the COVID-19 Pandemic: Development of a Public Coronavirus Twitter Data Set. 
    JMIR Public Health and Surveillance (2020). 
    See repo here: https://github.com/echen102/COVID-19-TweetIDs


Input data: 
    COVID2020 dataset
    Merged dataset files from Chen et al. 
        output by `1_merge_chen_etal.py`
        
Output:
    Data/Sec_3_COVID2020/stats/{start_date}_to_{end_date}.pickle 
        they contain comparison stats with existing dataset

Usage:
    `python Sec_3_COVID2020/2_dataset_stats.py`
'''


############ replace the path below ############

tweets_dir = 'COVID2020/'
opt_dir = 'Data/Sec_3_COVID2020/stats/'
chen_etal_data = 'Data/Sec_3_COVID2020/COVID-19-TweetIDs-merged/'
period = 0 # change this to a period index between 0 - 15, inclusively.

############ replace the path above ############

import os
import up
import bz2
import json
import time
import pickle

from collections import deque
from utils.config import ALL_DATES, VERBOSE

def calc_stats(tweets_dir, opt_dir, chen_etal_data, period):
    
    days_to_be_checked = ALL_DATES[period] 
    start_date = days_to_be_checked[0]
    end_date = days_to_be_checked[-1]

    start = time.time()
    filedeque = deque()
    
    date_to_coverage = dict()

    for subdir, _, files in os.walk(tweets_dir):
        for f in sorted(files):
            filename, filetype = f.split('.')
            if filetype == 'bz2':
                if filename[5:] in days_to_be_checked:
                    filepath = os.path.join(subdir, f)
                    filedeque.append(filepath)

    while filedeque:
            
        tweet_file = filedeque.popleft()
        tweet_file_date = tweet_file.split("/")[-1].split(".")[0][5:]
        kristina_data = f"{chen_etal_data}/{tweet_file_date}.txt"
        
        with open(kristina_data, "r") as f:
            kristina_tweet_ids = f.readlines() 
            kristina_tweet_ids = [tweet_id.strip() for tweet_id in kristina_tweet_ids if tweet_id.strip() != ""]
            kristina_tweet_ids = set(kristina_tweet_ids)

        try:
            with bz2.open(tweet_file, "rt") as bzinput:
                our_tweet_cnt = 0
                overlap_cnt = 0

                for i, line in enumerate(bzinput):

                    tweet = json.loads(line)

                    if "id_str" not in tweet:
                        continue

                    our_tweet_id = tweet["id_str"]
                    our_tweet_cnt += 1

                    if our_tweet_id in kristina_tweet_ids:
                        overlap_cnt += 1

                    if VERBOSE and (i+1) % VERBOSE == 0:
                        print('{0} {1} has been processed.'.format(tweet_file, i+1))

                stats= {
                    "our_total_tweet": our_tweet_cnt, 
                    "kristina_total_tweet": len(kristina_tweet_ids), 
                    "overlap_cnt": overlap_cnt,
                    "overlap_ratio_ours": overlap_cnt/our_tweet_cnt,
                    "overlap_ratio_kris": overlap_cnt/len(kristina_tweet_ids)
                }

                date_to_coverage[tweet_file] = stats

                print(tweet_file, stats)

        except EOFError:
            print("#"*60+"\n{0} encountered EOF error\n".format(tweet_file)+"#"*60)

        print("\n{0} HAS BEEN PROCESSED \n".format(tweet_file))
        
    end = time.time()
    print('\nRunning time: {:.2f} hours {:.2f} mins'.format((end-start)/3600, ((end-start)%3600)/60))


    with open( f"{opt_dir}/{start_date}_to_{end_date}.pickle" , "wb") as f:
        pickle.dump(date_to_coverage, f)


if __name__ == "__main__":

    if not os.path.isdir(opt_dir):
        os.makedirs(opt_dir)
        
    calc_stats(tweets_dir, opt_dir, chen_etal_data, period)
    