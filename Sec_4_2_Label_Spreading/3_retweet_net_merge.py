'''
For each selected country, merge within-country retweet network across multiple periods into one single retweet network

Input data:
    Data/Sec_4_2_Label_Spreading/retweet_net/{start_date}_{end_date}/{country}.csv 
        output by `2_retweet_net_extraction.py`
        
Output (under the given directory):
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/retweet_net.csv
        for each selected country, it contains duplicated edges without edge weight
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/retweet_net_weight.csv
        for each selected country, it contains deduplicated edges with edge weight
        
Example usage:
    `python Sec_4_2_Label_Spreading/3_retweet_net_merge.py`
'''

############ replace the path below ############

retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'

############ replace the path above ############


import os
import pandas as pd
import up
from collections import Counter
from utils.config import ALL_DATES, SELECTED_COUNTRIES


if not os.path.exists(f"{retweet_net_path}/Country_Network/"):
    os.mkdir(f"{retweet_net_path}/Country_Network/")

for country in SELECTED_COUNTRIES:
        
    columns = [ 'user_tweeting_id', 'user_tweeting_name', 'location', 'user_tweeted_id', 'user_tweeted_name', ]

    savepath = f"{retweet_net_path}/Country_Network/{country}"

    if not os.path.exists(f'{savepath}'):
        os.makedirs(f'{savepath}')

    with open(f'{savepath}/retweet_net.csv', 'w') as f:

        for month in range(len(ALL_DATES)):

            periods = ALL_DATES[month]
            start_date = periods[0]
            end_date = periods[-1]

            selected_period = f"{start_date}_to_{end_date}"

            filepath = f"{retweet_net_path}/{selected_period}/{country}.csv"
            df = pd.read_csv(filepath, names=columns, low_memory=False)

            for index, row in df.iterrows() :

                user_tweeting_id = row['user_tweeting_id']
                user_tweeted_id = row['user_tweeted_id']

                f.writelines( f"{user_tweeting_id}, {user_tweeted_id}\n" )
                
                
                
for country in SELECTED_COUNTRIES:
    
    filepath = f"{retweet_net_path}/{selected_period}/{country}.csv"
    
    Data = open(filepath, "r")
    edge_counts = Counter( (' '.join(line.strip().split(',')[:2][::-1]) for line in Data) )

    savepath = f"{retweet_net_path}/Country_Network/{country}"

    with open(f"{savepath}/retweet_net_weight.csv", 'w') as f:
        for edge, weight in edge_counts.items():
            f.write(f"{edge} {weight}\n")
