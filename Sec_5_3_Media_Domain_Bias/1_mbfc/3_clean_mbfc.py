'''
Clean up the MBFC data we have

Input data:
    Data/Sec_5_3_Media_Domain_Bias/mbfc_ratings.csv
        output by `1_scrape_mbfc_ratings.py`
    Data/Sec_5_3_Media_Domain_Bias/media_twitter_collections.csv
        output by `2_media_twitter_collection.py`
        
Output: 
    Data/Sec_5_3_Media_Domain_Bias/media_twitter_collections.csv

Usage:
    `python Sec_5_3_Media_Domain_Bias/1_mbfc/3_clean_mbfc.py`
'''

import pandas as pd
import re

path = 'Data/Sec_5_3_Media_Domain_Bias/mbfc_ratings.csv'
mbfc = pd.read_csv(path)


leaning_map = {'left': 'Left', 'leftcenter': 'Center-left', 'center-left': 'Center-left', 'extremeleft': 'Extreme-left',
               'right': 'Right', 'rightcenter': 'Center-right', 'center-right': 'Center-right', 'extremeright': 'Extreme-right',
               'center': 'Center'}


def get_leaning(x):
    cat = x['Category']
    if cat != 'fake-news':
        return leaning_map[ cat ]
    
    img = x['Img']
    if type(img) is str:
        img_ext = re.sub('[^a-zA-Z]+', '', img.split('.')[0])
        
        return leaning_map[img_ext] if img_ext in leaning_map else None
    else:
        None
        
        
mbfc['Ideology'] = mbfc.apply(lambda x: get_leaning(x), axis=1)
mbfc = mbfc[mbfc.Ideology.notnull()]

media_to_leaning = dict(zip( mbfc.Title, mbfc.Ideology ))

media_twitter_path = 'Data/Sec_5_3_Media_Domain_Bias/media_twitter_collections.csv'
media_twitter = pd.read_csv(media_twitter_path)

media_twitter['Ideology'] = media_twitter.Parent.apply(lambda x: media_to_leaning[x])
media_twitter.to_csv(media_twitter_path, index=False)