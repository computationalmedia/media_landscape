'''
Extract URLs shared from COVID2020

Input data:
    COVID2020 dataset
    Data/Sec_4_1_Geolocation/geoparse/merged_uid_to_world_loc_w_pol.pickle
        output by `Sec_4_1_Geolocation/7_add_politicians_to_geolocation.py`

Output:
    Data/Sec_4_3_URL_Extraction/URLs/{start_date}_{end_date}/{country}.csv 
        start_date and end_date is from the given period
        where country is from ['United States', 'United Kingdom', 'Canada', 'Australia', 'France', 'Germany', 'Spain', 'Turkey']
        each csv file has 5 columns: [tweet_id, user_id, username, location, url]
        
Usage:
    `python Sec_4_3_URL_Extraction/1_url_extraction.py`
    
'''

############ replace the path below ############

data_path = 'COVID2020/'
opt_path = 'Data/Sec_4_3_URL_Extraction/URLs/'
location_path = 'Data/Sec_4_1_Geolocation/geoparse/merged_uid_to_world_loc_w_pol.pickle'
period = 0 # change this to a period index between 0 - 15, inclusively.

############ replace the path above ############


import bz2
import json
import os
import up
import time
import csv
import pickle
from collections import deque
from utils.config import ALL_DATES, VERBOSE


class URLExtractor(object):
    
    def __init__(self, data_path=None, location_path=None, opt_dir=None, period=None):

        self.tweets_dir = data_path
        
        self.opt_dir = opt_dir
        if not self.opt_dir.endswith('/'):
            self.opt_dir += '/'

        self.month = period
        if period is not None:
            self.periods = ALL_DATES[self.month]
            self.start_date = self.periods[0]
            self.end_date = self.periods[-1]
            self.opt_dir += 'urls_{}_to_{}/'.format(self.start_date, self.end_date)

        if not os.path.isdir(self.opt_dir):
            os.makedirs(self.opt_dir)

        self.verbose = VERBOSE        

        with open(location_path, "rb") as f:
            self.user_id_to_country = pickle.load(f)

    def extract_urls_from_tweet(self, tweet):
        '''
        extract interaction targets
        '''

        is_quote = False
        quoted_id = None


        if 'quoted_status' in tweet.keys() and 'retweeted_status' not in tweet.keys():
            is_quote = True 
            quoted_id = tweet['quoted_status']['id_str']

        urls = self._extract_vids(tweet)

        external_urls = []

        # remove all urls related to quotes if it's already a quote
        for url in urls:
            if is_quote and quoted_id in url: # skip quoted link
                continue
            elif tweet['id_str'] in url: # avoid self-referencing urls
                continue

            external_urls.append( url )
    
        return external_urls

    def extract_urls(self):
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

                        username = tweet['user']['screen_name']
                        user_id = tweet['user']['id_str']
                        tweet_id = tweet['id_str']
                        
                        if tweet['user']['location'] is not None and user_id in self.user_id_to_country:
                            location = self.user_id_to_country[ user_id ]
                        else:  
                            continue

                        collected_urls = self.extract_urls_from_tweet(tweet) 
                        
                        if "quoted_status" in tweet: # pure quotes or retweets of quotes; look for urls in the quoted part
                            collected_urls = collected_urls + self.extract_urls_from_tweet(tweet['quoted_status']) 
                        elif "retweeted_status" in tweet: # pure retweets; look for urls in the original tweets
                            collected_urls = collected_urls + self.extract_urls_from_tweet(tweet['retweeted_status']) 

                        collected_urls = set( collected_urls )
                        
                        output_path = os.path.join(self.opt_dir+'{}.csv'.format(location))
                        with open(output_path, 'a') as ofile:
                            writer = csv.writer(ofile, delimiter=',')

                            for url in collected_urls:
                                rows_to_be_written = [tweet_id, user_id, username, location, url]
                                writer.writerow(rows_to_be_written)


            except EOFError:
                print("#"*60+"\n{0} encountered EOF error\n".format(tweet_file)+"#"*60)

            print("\n{0} HAS BEEN PROCESSED \n".format(tweet_file))

        end = time.time()
        print('\nExtraction time: {:.2f} hours {:.2f} mins'.format((end-start)/3600, ((end-start)%3600)/60))


    def _expanded_urls(self, urls):
        expanded_urls = set()
        for url in urls:
            if url['expanded_url'] is not None:
                expanded_urls.add(url['expanded_url'])

        return expanded_urls

    def _extract_vids(self, tweet):
        original_urls = [] 
        try:
            for url in tweet['entities']['urls']:
                original_urls.append(url)
        except KeyError:
            pass
        try:
            for url in tweet['entities']['extended_tweet']['urls']:
                original_urls.append(url)
        except KeyError:
            pass

        original_vids = self._expanded_urls(original_urls) 
        return original_vids
 

if __name__ == "__main__":

    if not os.path.isdir(opt_path):
        os.makedirs(opt_path)

    extractor = URLExtractor(data_path=data_path, location_path=location_path, opt_dir=opt_path, period=period)

    extractor.extract_urls()
