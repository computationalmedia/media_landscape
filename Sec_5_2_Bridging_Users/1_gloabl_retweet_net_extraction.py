'''
For a given period, extract retweet network for a list of countries, where cross-country retweets are allowed
The script needs to be call on all 16 periods to obtain the complete retweet net

Input data:
    COVID2020 dataset
    Data/Sec_4_1_Geolocation/geoparse/merged_uid_to_world_loc_w_pol.pickle
        output by `Sec_4_1_Geolocation/7_add_politicians_to_geolocation.py`
Output:
    Data/Sec_4_2_Label_Spreading/retweet_net_global/gloabl_retweet_net.csv
        it has 5 columns: user_tweeting_id, user_tweeting_name, location, user_tweeted_id, user_tweeted_name, user_tweeted_location

Example usage:
    `python Sec_5_2_Bridging_Users/1_gloabl_retweet_net_extraction.py  `
'''

############ replace the path below ############

data_path = 'COVID2020/'
opt_path = 'Data/Sec_4_2_Label_Spreading/retweet_net_global/'
location_path = 'Data/Sec_4_1_Geolocation/geoparse/merged_uid_to_world_loc_w_pol.pickle'
period = 0 # change this to a period index between 0 - 15, inclusively.

############ replace the path above ############


import bz2
import json
import pickle
import os
import time
import csv
import up

from collections import deque

from utils.config import ALL_DATES, SELECTED_COUNTRIES, VERBOSE

class RetweetExtractor(object):
    
    def __init__(self, tweets_path=None, location_path=None, opt_dir=None, period=None,):

        self.tweets_dir = tweets_path        
        
        self.opt_dir = opt_dir
        if not self.opt_dir.endswith('/'):
            self.opt_dir += '/'
        
        self.period = period
        if period is not None:
            self.periods = ALL_DATES[self.period]
            self.start_date = self.periods[0]
            self.end_date = self.periods[-1]
            self.opt_dir += 'locations_{}_to_{}/'.format(self.start_date, self.end_date)

        if not os.path.isdir(self.opt_dir):
            os.makedirs(self.opt_dir)

        print("self.opt_dir: ", self.opt_dir)

        self.verbose = VERBOSE        

        with open(location_path, "rb") as f:
            self.user_id_to_country = pickle.load(f)

        self.selected_countries = SELECTED_COUNTRIES

    def extract_retweets(self):
        start = time.time()
        filedeque = deque()
        
        for subdir, _, files in os.walk(self.tweets_dir):
            for f in sorted(files):
                filename, filetype = f.split('.')
                if filetype == 'bz2':
                    if (self.month is not None and filename[5:] in self.periods) or (self.month is None):
                        filepath = os.path.join(subdir, f)
                        filedeque.append(filepath)

        output_path = os.path.join(self.opt_dir+'gloabl_retweet_net.csv')

        while filedeque:
            tweet_file = filedeque.popleft()

            try:
                with bz2.open(tweet_file, "rt") as bzinput:
                    for i, line in enumerate(bzinput):
                        tweet = json.loads(line)

                        if self.verbose and (i+1) % self.verbose == 0:
                            print('{0} {1} has been processed.'.format(tweet_file, i+1))
                            self.logger.info('{0} {1} has been processed.'.format(tweet_file, i))

                        if 'user' not in tweet.keys():
                            continue

                        user_tweeting_id = tweet['user']['id_str']
                        user_tweeting_name = tweet['user']['screen_name']

                        if 'retweeted_status' in tweet.keys() and 'quoted_status' not in tweet.keys():
                            if 'user' not in tweet['retweeted_status']:
                                continue
                            user_tweeted_id = tweet['retweeted_status']['user']['id_str']
                            user_tweeted_name = tweet['retweeted_status']['user']['screen_name']
                        else:
                            continue

                        if user_tweeting_id == user_tweeted_id: # avoid self loops
                            continue

                        if user_tweeting_id in self.user_id_to_country:
                            location = self.user_id_to_country[ user_tweeting_id ]
                        else:  
                            continue

                        if user_tweeted_id in self.user_id_to_country:
                            user_tweeted_location = self.user_id_to_country[ user_tweeted_id ]
                        else:
                            continue 

                        if location not in self.selected_countries or user_tweeted_location not in self.selected_countries:
                            continue
                       
                        with open(output_path, 'a') as ofile:
                            writer = csv.writer(ofile, delimiter=',')

                            rows_to_be_written = [ user_tweeting_id, user_tweeting_name, location, 
                                                   user_tweeted_id, user_tweeted_name, user_tweeted_location ]

                            writer.writerow(rows_to_be_written)
            
            except EOFError:
                print("#"*60+"\n{0} encountered EOF error\n".format(tweet_file)+"#"*60)

            print("\n{0} HAS BEEN PROCESSED \n".format(tweet_file))

        end = time.time()
        print('\nExtraction time: {:.2f} hours {:.2f} mins'.format((end-start)/3600, ((end-start)%3600)/60))


if __name__ == "__main__":

    
    if not os.path.isdir(opt_path):
        os.makedirs(opt_path)

    extractor = RetweetExtractor(tweets_path=data_path, location_path=location_path, opt_dir=opt_path, period=period, )

    extractor.extract_retweets()
