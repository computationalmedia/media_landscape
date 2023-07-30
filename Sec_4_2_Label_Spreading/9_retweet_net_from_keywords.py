'''
For a given period, extract within-country retweet network for a list of countries at once
The script needs to be call on all 16 periods to obtain the complete retweet net

Input data:
    COVID2020 dataset
    Data/Sec_4_1_Geolocation/geoparse/merged_uid_to_world_loc_w_pol.pickle
        output by `7_add_politicians_to_geolocation.py`
Output (under the given directory):
    Data/Sec_4_2_Label_Spreading/retweet_net_keyword/{start_date}_{end_date}/{country}.csv 
        start_date and end_date is from the given period
        where country is from ['United States', 'United Kingdom', 'Canada', 'Australia', 'France', 'Germany', 'Spain', 'Turkey']
        each csv file has 5 columns: user_tweeting_id, user_tweeting_name, location, user_tweeted_id, user_tweeted_name

Example usage:
    `python Sec_4_2_Label_Spreading/9_retweet_net_from_keywords.py`
'''

############ replace the path below ############

data_path = 'COVID2020/'
opt_path = 'Data/Sec_4_2_Label_Spreading/retweet_net_keyword/'
hashtag_folder = 'Data/Sec_4_2_Label_Spreading/'
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
    
    def __init__(self, tweets_path=None, hashtag_folder=None, location_path=None, opt_dir=None, period=None):

        self.tweets_dir = tweets_path        
        
        self.opt_dir = opt_dir

        if not os.path.exists(self.opt_dir):
            os.makedirs(self.opt_dir)
        
        self.month = period
        if period is not None:
            self.periods = ALL_DATES[self.period]
            self.start_date = self.periods[0]
            self.end_date = self.periods[-1]

            self.opt_dir = os.path.join( self.opt_dir, '{}_to_{}/'.format(self.start_date, self.end_date)  )
            
            if not os.path.exists(self.opt_dir):
                os.makedirs(self.opt_dir)

        self.verbose = VERBOSE        

        with open(location_path, "rb") as f:
            self.user_id_to_country = pickle.load(f)

        self.selected_countries = SELECTED_COUNTRIES

    
        with open(f'{hashtag_folder}/left_hashtags.csv', 'r') as f:
            left_hashtags = f.readlines()
            self.left_hashtags = set( [i.strip() for i in left_hashtags] )        
       
        with open(f'{hashtag_folder}/right_hashtags.csv', 'r') as f:
            right_hashtags = f.readlines()
            self.right_hashtags = set( [i.strip() for i in right_hashtags] )


    def extract_left_hashtags(self, hashtags_to_extract):
        
        candidicate_hashtags = [  tag.replace("#", "").replace(",", "").replace(".", "").replace(";", "").lower().strip() 
                                    for tag in hashtags_to_extract ]
        candidicate_hashtags = set(candidicate_hashtags)

        overlap = candidicate_hashtags & self.left_hashtags

        return overlap


    def extract_right_hashtags(self, hashtags_to_extract):

        candidicate_hashtags = [  tag.replace("#", "").replace(",", "").replace(".", "").replace(";", "").lower().strip()
                                     for tag in hashtags_to_extract ]
        candidicate_hashtags = set(candidicate_hashtags)

        overlap = candidicate_hashtags & self.right_hashtags

        return overlap
    
    
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
        
        while filedeque:
            tweet_file = filedeque.popleft()

            try:
                with bz2.open(tweet_file, "rt") as bzinput:
                    for i, line in enumerate(bzinput):
                        tweet = json.loads(line)

                        if self.verbose and (i+1) % self.verbose == 0:
                            print('{0} {1} has been processed.'.format(tweet_file, i+1))

                        if 'user' not in tweet.keys():
                            continue

                        user_tweeting_id = tweet['user']['id_str']
                        user_tweeting_profile = tweet['user']['description'] if tweet['user']['description'] is not None else ''

                        if 'retweeted_status' in tweet.keys() and 'quoted_status' not in tweet.keys():
                            if 'user' not in tweet['retweeted_status']:
                                continue
                            user_tweeted_id = tweet['retweeted_status']['user']['id_str']
                            user_tweeted_profile = tweet['retweeted_status']['user']['description'] if tweet['retweeted_status']['user']['description'] is not None else ''
                        else:
                            continue

                        if user_tweeting_id == user_tweeted_id: # avoid self loops
                            continue

                        # note: for now, we only make sure the user retweeting someone else has a location
                        if user_tweeting_id in self.user_id_to_country:
                            location = self.user_id_to_country[ user_tweeting_id ]
                        else:  
                            continue

                        if user_tweeted_id in self.user_id_to_country:
                            user_tweeted_location = self.user_id_to_country[ user_tweeted_id ]
                        else:
                            continue

                        if location != 'United States' or user_tweeted_location != 'United States':
                            continue

                        tweeting_user_overlap_with_left = self.extract_left_hashtags(user_tweeting_profile.split())
                        tweeting_user_overlap_with_right = self.extract_right_hashtags(user_tweeting_profile.split())

                        tweeted_user_overlap_with_left = self.extract_left_hashtags(user_tweeted_profile.split())
                        tweeted_user_overlap_with_right = self.extract_right_hashtags(user_tweeted_profile.split())

                        output_path = os.path.join(self.opt_dir+'{}.csv'.format(location))
                        with open(output_path, 'a') as ofile:
                            writer = csv.writer(ofile, delimiter=',')

                            rows_to_be_written = [ user_tweeting_id, user_tweeted_id, 
                                                   tweeting_user_overlap_with_left, tweeting_user_overlap_with_right, 
                                                   tweeted_user_overlap_with_left, tweeted_user_overlap_with_right, ]

                            writer.writerow(rows_to_be_written)


            
            except EOFError:
                print("#"*60+"\n{0} encountered EOF error\n".format(tweet_file)+"#"*60)

            print("\n{0} HAS BEEN PROCESSED \n".format(tweet_file))

        end = time.time()
        print('\nExtraction time: {:.2f} hours {:.2f} mins'.format((end-start)/3600, ((end-start)%3600)/60))


if __name__ == "__main__":

    extractor = RetweetExtractor(tweets_path=data_path, hashtag_folder=hashtag_folder, location_path=location_path, 
                                 opt_dir=opt_path, period=period, )

    extractor.extract_retweets()
