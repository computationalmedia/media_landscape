'''
Extract language associated with tweets from users with a geolocation

Input data:
    COVID2020 dataset
    Data/Sec_4_1_Geolocation/geoparse/merged_uid_to_world_loc_w_pol.pickle
        output by `7_add_politicians_to_geolocation.py`
        
Output:
    Data/Sec_4_1_Geolocation/lang_stats/lang_stats_{start_date}_{end_date}.pickle
    
Usage:
    `python Sec_4_1_Geolocation/8_lang_stats.py `
'''

############ replace the path below ############

data_path = 'COVID2020/'
opt_path = 'Data/Sec_4_1_Geolocation/lang_stats/'
location_path='Data/Sec_4_1_Geolocation/geoparse/merged_uid_to_world_loc_w_pol.pickle'
period = 0 # change this to a period index between 0 - 15, inclusively.

############ replace the path above ############


import bz2
import json
import os
import up
import time
import pickle

from collections import defaultdict, deque

from utils.config import ALL_DATES, VERBOSE

class StatsChecker(object):
    
    def __init__(self, data_dir=None, opt_dir=None, location_path=None, verbose=None, period=None):
        self.period = period       

        self.periods = ALL_DATES[self.period] 
        self.start_date = self.periods[0]
        self.end_date = self.periods[-1]

        if not os.path.isdir(opt_dir):
            os.makedirs(opt_dir)

        self.data_dir = data_dir
        self.opt_dir = opt_dir
        
        self.location_path = location_path
        self.verbose = verbose 

        with open(self.location_path, "rb") as f:
            self.users_with_unq_loc = pickle.load(f)

    def check_stats(self):
        
        start = time.time()
        filedeque = deque()

        for subdir, _, files in os.walk(self.data_dir):
            for f in sorted(files):
                filename, filetype = f.split('.')
                if filetype == 'bz2' and filename[5:] in self.periods:
                    filepath = os.path.join(subdir, f)
                    filedeque.append(filepath)
        
        date_to_country_to_tweet_languages = dict()

        while filedeque:
            tweet_file = filedeque.popleft()

            try:
                with bz2.open(tweet_file, "rt") as bzinput:

                    country_to_tweet_languages = defaultdict()

                    for i, line in enumerate(bzinput):
                        tweet = json.loads(line)

                        if 'user' not in tweet.keys():
                            continue
                        
                        uid = tweet['user']['id_str']

                        if uid not in self.users_with_unq_loc:
                            continue

                        user_country = self.users_with_unq_loc[uid]

                        if 'quoted_status' in tweet:
                            tweet_language = tweet['quoted_status']['lang']
                        else:
                            tweet_language = tweet['lang']

                        if user_country not in country_to_tweet_languages:
                            country_to_tweet_languages[user_country] = {tweet_language: 1}
                        else:
                            if tweet_language not in country_to_tweet_languages[user_country]:
                                country_to_tweet_languages[user_country][tweet_language] = 1
                            else:
                                country_to_tweet_languages[user_country][tweet_language] += 1

                        if (i+1) % self.verbose == 0:
                            print('{0} {1} has been processed.'.format(tweet_file, i+1))

                    date_to_country_to_tweet_languages[tweet_file] = country_to_tweet_languages
                    
            except EOFError:
                print("#"*60+"\n{} encountered EOF error\n".format(tweet_file)+"#"*60)

            print("\n{} HAS BEEN PROCESSED \n".format(tweet_file))
        

        end = time.time()

        output_path = os.path.join(self.opt_dir+'lang_stats_{}_{}.pickle'.format(self.start_date, self.end_date))
        with open(output_path, 'wb') as f:
            pickle.dump(date_to_country_to_tweet_languages, f)

        print('\nRunning time: {:.2f} hours {:.2f} mins'.format((end-start)/3600, ((end-start)%3600)/60))
        

if __name__ == "__main__":

    processor = StatsChecker(data_dir=data_path, opt_dir=opt_path, location_path=location_path, verbose=VERBOSE, period=period)

    processor.check_stats()