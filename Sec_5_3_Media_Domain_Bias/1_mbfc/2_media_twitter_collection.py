'''
Note: The following is written based on Twitter v1.1

Search for Twitter accounts by querying Twitter search API with media titles.
For each media outlet, it finds the most similar user profile by performing URL checks

Input data:
    Data/Sec_5_3_Media_Domain_Bias/mbfc_ratings.csv
        output by `1_scrape_mbfc_ratings.py`
    Data/Sec_5_3_Media_Domain_Bias/key.json
        users shall provide it themselevs throught Twitter development program
        it should contain API key, API secret key, access token and secret access token
        
Output:
    Data/Sec_5_3_Media_Domain_Bias/media_twitter_collections.csv

Usage:
    `python Sec_5_3_Media_Domain_Bias/1_mbfc/2_media_twitter_collection.py`
'''


############ replace the path below ############

key_path = 'Data/Sec_5_3_Media_Domain_Bias/keys.json' # replace this by your own Twitter keys

############ replace the path above ############


import sys, os, json, tldextract, csv, time
import tldextract, requests
from tqdm import tqdm
import pandas as pd
from tweepy import OAuthHandler, API

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))


def get_user_profile_url(user_json):
    expand_urls = []

    if 'entities' in user_json:
        if 'url' in user_json['entities']:
            if 'urls' in user_json['entities']['url']:
                if len(user_json['entities']['url']['urls']) > 0:
                    if 'expanded_url' in user_json['entities']['url']['urls'][0]:
                        if user_json['entities']['url']['urls'][0]['expanded_url'] is not None:
                            expand_url = user_json['entities']['url']['urls'][0]['expanded_url'].lower()
                            if expand_url is not None:
                                expand_urls.append(expand_url)

        if 'description' in user_json['entities']:
            if 'urls' in user_json['entities']['description']:
                if len(user_json['entities']['description']['urls']) > 0:
                    if 'expanded_url' in user_json['entities']['description']['urls'][0]:
                        if user_json['entities']['description']['urls'][0]['expanded_url'] is not None:
                            expand_url = user_json['entities']['description']['urls'][0]['expanded_url'].lower()
                            if expand_url is not None:
                                expand_urls.append(expand_url)


    return expand_urls


def replace_country(x):
    if type(x) is float:
        return 'Unknown'
    if 'USA' in x:
        return 'United States'
    elif 'UK' in x:
        return 'United Kingdom'
    elif 'Czech Republic' in x:
        return 'Czechia'
    elif 'Hong King' in x:
        return 'Hong Kong'
    elif 'South Korea' in x:
        return 'Korea, South'
    elif 'North Korea' in x:
        return 'Korea, North'
    elif 'UAE' in x:
        return 'United Arab Emirates'
    else:
        return x


def clean_suffix(url):
    if url.endswith('/new'):
        url = url[:-4]
    elif url.endswith('/news'):
        url = url[:-5]
    else:
        url = url
    return url

def reconstruct_url(url):

    url_domain = tldextract.extract(url).domain
    url_subdomain = tldextract.extract(url).subdomain
    url_suffix = tldextract.extract(url).suffix

    if url_subdomain == 'www' or url_subdomain == 'com' or url_subdomain == 'http' or url_subdomain == 'https':
        url_subdomain = ''

    if url_suffix == 'www' or url_suffix == 'com' or url_suffix == 'http' or url_suffix == 'https':
        url_suffix = ''

    user_profile_url_reconstruct = url_domain 

    if url_subdomain != '':
        user_profile_url_reconstruct += '.'+url_subdomain

    if url_suffix != '':
        user_profile_url_reconstruct += '.'+url_suffix

    user_profile_url_reconstruct = user_profile_url_reconstruct.strip()

    return user_profile_url_reconstruct


def main():
    
    with open(key_path, 'r') as fin:
        key_dict = json.load(fin)

    consumer_key = key_dict['API key']
    consumer_secret = key_dict['API secret key']
    access_token = key_dict['Access token']
    access_token_secret = key_dict['Access token secret']

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth, wait_on_rate_limit=True)

    num_hit_twitter = 0
    num_fail_twitter = 0
    num_request = 0

    media_df = pd.read_csv('Data/Sec_5_3_Media_Domain_Bias/mbfc_ratings.csv')
    media_df['Country'] = media_df['Country'].apply(lambda x: replace_country(x))

    print('media_df shape: ', media_df.shape)

    media_url_to_name = dict(zip(media_df.URL.values, media_df.Title.values))
    media_url_to_country = dict(zip(media_df.URL.values, media_df.Country.values))
    media_url_to_leaning = dict(zip(media_df.URL.values, media_df.Ideology.values))

    media_name_to_twitter = dict()

    # searching Twitter Search API for tweet handles if we cannot find it on webpage
    print('{} media in total to be searched'.format(len(media_url_to_name)))

    start_time = time.time()

    for curr_website_url, media in tqdm(media_url_to_name.items()):
    # for curr_website_url, media in tmp_media_list.items():

        website_url = clean_suffix(curr_website_url)

        try:
            r = requests.get(website_url, verify=False, timeout=5)
            website_url_redirect = r.url
        except:
            website_url_redirect = website_url

        url_reconstruct = reconstruct_url(website_url)
        url_reconstruct_redirect = reconstruct_url(website_url_redirect)

        seq_match = 0
        most_similar_handle = []

        returned_users = api.search_users(media, count=10)  
        num_request += 1
        url_found = False

        for user in returned_users:
            user_json = user._json
            
            user_name = user_json['name']
            screen_name = user_json['screen_name'].lower()
            # print('user name: {} screen name: {}'.format(user_name, screen_name) )
            location = user_json['location'] if 'location' in user_json else 'Unavailable'

            if location.startswith('"'):
                location = location[1:]
            if location.endswith('"'):
                location = location[:-1]
            location = location.strip()

            user_profile_url_list = get_user_profile_url(user_json)

            if len(user_profile_url_list):

                found = False

                for user_profile_url_origin in user_profile_url_list:
                    
                    user_profile_url = clean_suffix(user_profile_url_origin)
                    user_profile_url_reconstruct = reconstruct_url(user_profile_url)

                    # print( 'given url: {} ; current url from user profile: {}; '.format(url_reconstruct, user_profile_url_reconstruct) )

                    if user_profile_url_reconstruct == url_reconstruct or user_profile_url_reconstruct == url_reconstruct_redirect:
                        seq_match += 1
                        most_similar_handle.append( (user_name, screen_name, user_profile_url_origin, location ) )
                        found = True
                        break
                    
                if not found:
                    
                    for user_profile_url_origin in user_profile_url_list:
                        
                        user_profile_url = clean_suffix(user_profile_url_origin)

                        try:
                            r = requests.get(user_profile_url, verify=False, timeout=0.1)
                            user_profile_url = r.url
                        except:
                            user_profile_url = user_profile_url

                        user_profile_url_reconstruct = reconstruct_url(user_profile_url)

                        if user_profile_url_reconstruct == url_reconstruct or user_profile_url_reconstruct == url_reconstruct_redirect:
                            seq_match += 1
                            most_similar_handle.append( (user_name, screen_name, user_profile_url_origin, location ) )
                            break
            
        media_name_to_twitter[ (media, curr_website_url, url_reconstruct, url_reconstruct_redirect)  ] = most_similar_handle

        if not most_similar_handle:
            num_fail_twitter += 1

    end_time = time.time()
    print('Total time: ', end_time-start_time)

    print('number of requests sent: {0}'.format(num_request))
    print('{} fails'.format(num_fail_twitter))
    print('{} found in total'.format(len(media_name_to_twitter)))

    with open("data/media_twitter_collections.csv", 'w') as ofile:
        writer = csv.writer(ofile, delimiter=',')
        writer.writerow(['Title', 'twitter', 'Ideology', 'URL', 'URL Reconstruct', 'URL Redirect Reconstruct', 'Location', 'Parent', 'Parent URL', 'Parent Country'])

        for (parent_media, media_url, url_reconstruct, url_reconstruct_redirect), matching_twitter_url in media_name_to_twitter.items():
            country = media_url_to_country[media_url]
            leaning = media_url_to_leaning[media_url]

            for user_name, screen_name, url, location in matching_twitter_url:
                rows_to_be_written = [user_name, screen_name, leaning, url, url_reconstruct, url_reconstruct_redirect, location, parent_media, media_url, country]
                writer.writerow(rows_to_be_written)

if __name__ == '__main__':
    main()