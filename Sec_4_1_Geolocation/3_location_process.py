'''
Extract Twitter users' locations from their profiles

Input data:
    COVID2020 dataset
Output: 
    Data/Sec_4_1_Geolocation/user_locations/merged_unique_locations.pickle
    Data/Sec_4_1_Geolocation/user_locations/user_locations_multiple_period.csv
    + several immediate pickle and csv files
    
Example usage:
    Extraction:
    `python Sec_4_1_Geolocation/2_location_process.py`
    
    Merge after extraction is done on all periods (after setting merge=True):
    `python Sec_4_1_Geolocation/2_location_process.py`
'''

############ replace the path below ############

data_path = 'COVID2020/'
opt_path = 'Data/Sec_4_1_Geolocation/user_locations/'
period = 0 # change this to a period index between 0 - 15, inclusively.
merge = False # change this to merge after extraction is done on all periods

############ replace the path above ############


import bz2
import json
import pandas as pd
import os
import up
import time
import csv
import pickle

from collections import defaultdict, deque

from utils.config import ALL_DATES, VERBOSE


class LocationProcessor(object):
    
    def __init__(self, data_dir=None, opt_dir=None, verbose=None, period=None):
        self.period = period       

        self.periods = ALL_DATES[self.period] 
        self.start_date = self.periods[0]
        self.end_date = self.periods[-1]

        if not os.path.isdir(opt_dir):
            os.makedirs(opt_dir)

        self.data_dir = data_dir
        self.opt_dir = opt_dir
        self.verbose = verbose 

    def extract_user_locations(self):
        
        start = time.time()
        filedeque = deque()

        user_to_location = defaultdict(lambda: set())

        for subdir, _, files in os.walk(self.data_dir):
            for f in sorted(files):
                filename, filetype = f.split('.')
                if filetype == 'bz2' and filename[5:] in self.periods:
                    filepath = os.path.join(subdir, f)
                    filedeque.append(filepath)
        
        while filedeque:
            tweet_file = filedeque.popleft()

            try:
                with bz2.open(tweet_file, "rt") as bzinput:
                    for i, line in enumerate(bzinput):
                        tweet = json.loads(line)

                        if 'user' not in tweet.keys():
                            continue
                        
                        uid = tweet['user']['id_str']

                        if tweet['user']['location'] is not None:
                            user_to_location[uid].add(tweet['user']['location'].lower())

                        if 'retweeted_status' in tweet.keys() and tweet['retweeted_status']['user']['location'] is not None:
                            user_to_location[tweet['retweeted_status']['user']['id_str']].add(tweet['retweeted_status']['user']['location'].lower())

                        if 'quoted_status' in tweet.keys() and tweet['quoted_status']['user']['location'] is not None:
                            user_to_location[tweet['quoted_status']['user']['id_str']].add(tweet['quoted_status']['user']['location'].lower())

                        if i % self.verbose == 0:
                            print('{} has been processed.'.format(i))
                
            except EOFError:
                print("#"*60+"\n{} encountered EOF error\n".format(tweet_file)+"#"*60)

            print("\n{} HAS BEEN PROCESSED \n".format(tweet_file))
        

        end = time.time()
        print('\nExtraction time: {:.2f} hours {:.2f} mins'.format((end-start)/3600, ((end-start)%3600)/60))
        
        print('\nStart writing to csv')

        start = time.time()
        output_path = os.path.join(self.opt_dir+'user_locations_{}_{}.csv'.format(self.start_date, self.end_date))
        with open(output_path, 'w') as ofile:
            writer = csv.writer(ofile, delimiter=',')
            writer.writerow(['user_id','locations'])
            for key in user_to_location:
                writer.writerow([key, user_to_location[key]])

        df = pd.read_csv(self.opt_dir+'user_locations_{}_{}.csv'.format(self.start_date, self.end_date))
        df.set_index([df.columns.values[0]], inplace=True)
        df.index.names = [None]

        unique_locations = set()
        non_empty_cnt = 0
        df_loc = df.locations.values

        for loc in df_loc:
            if loc == 'set()':
                continue
            non_empty_cnt += 1
            loc_eval = eval(loc)
            for l in loc_eval:
                unique_locations.add(l)

        print('reduction rate: {}'.format(1-len(unique_locations)/non_empty_cnt))

        dict_pickle_path = os.path.join(self.opt_dir+'unique_locations_{}_{}.pickle'.format(self.start_date, self.end_date))
        with open(dict_pickle_path, 'wb') as handle:
            pickle.dump(list(unique_locations), handle, protocol=pickle.HIGHEST_PROTOCOL)

        end = time.time()
        print('\nWriting time: {:.2f} hours {:.2f} mins'.format((end-start)/3600, ((end-start)%3600)/60))
        

    def merge_user_locations(self):
        
        merged_savepath = f"{self.opt_dir}/merged/"

        if not os.path.exists(merged_savepath):
            os.mkdir(merged_savepath)
            
        unique_loc = set()
        total_cnt = 0
        
        dates = ALL_DATES[0]
        base_loc_path = f'{self.opt_dir}/unique_locations_{dates[0]}_{dates[-1]}.pickle'
        with open(base_loc_path, 'rb') as handle:
            unique_loc = set(pickle.load(handle))
            total_cnt += len(unique_loc)

        for dates in ALL_DATES[1:]:
            loc_path = f'{self.opt_dir}/unique_locations_{dates[0]}_{dates[-1]}.pickle'
            with open(loc_path, 'rb') as handle:
                curr_unique_loc = pickle.load(handle)
                unique_loc |= set(curr_unique_loc)
                total_cnt += len(curr_unique_loc)

        with open(merged_savepath+'merged_unique_locations.pickle', 'wb') as handle:
            pickle.dump(list(unique_loc), handle, protocol=pickle.HIGHEST_PROTOCOL)

        print('merged size: ', len(unique_loc))
        print('reduced size: ', 1-len(unique_loc)/total_cnt)


        dates = ALL_DATES[0]
        base_path = f'{self.opt_dir}/user_locations_{dates[0]}_{dates[-1]}.csv'
        base_df = pd.read_csv(base_path)

        for dates in ALL_DATES[1:]:
            loc_path = f'{self.opt_dir}/user_locations_{dates[0]}_{dates[-1]}.csv'
            loc_df = pd.read_csv(loc_path)
            base_df = base_df.append(loc_df, ignore_index=True)
        
        base_df = base_df.reset_index(drop=True)

        base_df.to_csv(f"{merged_savepath}/user_locations_multiple_period.csv")


if __name__ == "__main__":
    
    if not os.path.isdir(opt_path):
        os.makedirs(opt_path)
    
    processor = LocationProcessor(in_dir=data_path, opt_dir=opt_path, verbose=VERBOSE, period=period)

    # first extract user locations from their profiles
    # save them period by period
    if not merge:
        processor.extract_user_locations()
    
    # then merge user locations from different periods together
    # this final merged file will be the one we need
    # NOTE: this function assumes extract_user_locations() has been execuated on ALL PERIODS!
    else:
        processor.merge_user_locations()
