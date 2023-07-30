'''
Extract geotags from tweets.

Input data:
    COVID2020 dataset
    
Output: 
    Data/Sec_4_1_Geolocation/geotags/users_geotag_{start_date}_{end_date}.pickle
        it contains place attributes for users within a given period
    Data/Sec_4_1_Geolocation/geotags/geotag_stats_{start_date}_{end_date}.pickle
        it contains the number of tweets containing `place` attributes within a given period

Usage:
    `python Sec_4_1_Geolocation/1_geotag_extraction.py`
'''

############ replace the path below ############

data_path = 'COVID2020/'
opt_path = 'Data/Sec_4_1_Geolocation/geotags/'
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



class GeotagExtractor(object):
    
    def __init__(self, data_dir=None, opt_dir=None, verbose=None, period=None):
        self.period = period       

        self.periods = ALL_DATES[self.period] 
        self.start_date = self.periods[0]
        self.end_date = self.periods[-1]

        if not opt_dir.endswith('/'):
            opt_dir += '/'

        if not os.path.isdir(opt_dir):
            os.makedirs(opt_dir)

        self.data_dir = data_dir
        self.opt_dir = opt_dir
        
        self.verbose = verbose 

        self.place_attributes = ['id', 'place_type', 'name', 'full_name', 'country_code', 'country']
        
        
    def extract_geo_tags(self):
        
        start = time.time()
        filedeque = deque()

        user_to_location = defaultdict(set)

        for subdir, _, files in os.walk(self.data_dir):
            for f in sorted(files):
                filename, filetype = f.split('.')
                if filetype == 'bz2' and filename[5:] in self.periods:
                    filepath = os.path.join(subdir, f)
                    filedeque.append(filepath)
        

        date_to_tweets = dict()

        while filedeque:
            tweet_file = filedeque.popleft()

            try:
                with bz2.open(tweet_file, "rt") as bzinput:

                    tweet_counter = 0

                    for i, line in enumerate(bzinput):
                        tweet = json.loads(line)

                        if 'user' not in tweet.keys():
                            continue
                        
                        uid = tweet['user']['id_str']

                        if tweet['place'] is not None and len(tweet['place']) > 0:
                            tweet_counter += 1

                            place_to_save = tuple( tweet['place'][attr] for attr in self.place_attributes )
                            user_to_location[uid].add( place_to_save )

                        if 'retweeted_status' in tweet.keys() and tweet['retweeted_status']['place'] is not None and \
                            len(tweet['retweeted_status']['place']) > 0:

                            place_to_save = tuple( tweet['retweeted_status']['place'][attr] for attr in self.place_attributes )
                            user_to_location[tweet['retweeted_status']['user']['id_str']].add( place_to_save )

                        if 'quoted_status' in tweet.keys() and tweet['quoted_status']['place'] is not None and \
                            len(tweet['quoted_status']['place']) > 0:
                            
                            place_to_save = tuple( tweet['quoted_status']['place'][attr] for attr in self.place_attributes )
                            user_to_location[tweet['quoted_status']['user']['id_str']].add( place_to_save )

                        if (i+1) % self.verbose == 0:
                            print('{0} {1} has been processed.'.format(tweet_file, i+1))

                    date_to_tweets[tweet_file] = tweet_counter
                    
            except EOFError:
                print("#"*60+"\n{} encountered EOF error\n".format(tweet_file)+"#"*60)

            print("\n{} HAS BEEN PROCESSED \n".format(tweet_file))
        

        end = time.time()
        print('\nExtraction time: {:.2f} hours {:.2f} mins'.format((end-start)/3600, ((end-start)%3600)/60))

        start = time.time()
        output_path = os.path.join(self.opt_dir+'users_geotag_{}_{}.pickle'.format(self.start_date, self.end_date))
        with open(output_path, 'wb') as f:
            pickle.dump(user_to_location, f)
        
        output_path = os.path.join(self.opt_dir+'geotag_stats_{}_{}.pickle'.format(self.start_date, self.end_date))
        with open(output_path, 'wb') as f:
            pickle.dump(date_to_tweets, f)
        
        end = time.time()
        print('\nExtraction time: {:.2f} hours {:.2f} mins'.format((end-start)/3600, ((end-start)%3600)/60))
            


if __name__ == "__main__":

    if not os.path.isdir(opt_path):
        os.makedirs(opt_path)
        
    extractor = GeotagExtractor(in_dir=data_path, opt_dir=opt_path, verbose=VERBOSE, period=period)

    extractor.extract_geo_tags()