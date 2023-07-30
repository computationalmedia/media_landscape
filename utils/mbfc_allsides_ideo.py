import pandas as pd

media_twitter_path = 'Data/Sec_5_3_Media_Domain_Bias/media_twitter_collections_with_bias.csv'

media_twitter = pd.read_csv(media_twitter_path)
media_twitter = media_twitter[ (media_twitter['Parent Country'] != 'Unknown') ]

# manual change nextnewsnetwork channel on youtube
media_twitter.loc[media_twitter.URL.str.contains('youtube'), 'URL Reconstruct'] = 'nextnewsnetwork'
media_twitter.loc[media_twitter.URL.str.contains('youtube'), 'URL Redirect Reconstruct'] = 'nextnewsnetwork'


ideo_to_abbrev = {'Extreme-left': 'EL', 'Left': 'L', 'Center-left': 'CL', 'Center': 'C', 
                  'Center-right': 'CR', 'Right': 'R', 'Extreme-right': 'ER'}
media_twitter['Ideology_short'] = media_twitter.Ideology.apply(lambda x: ideo_to_abbrev[x])

url_to_label = dict(zip(media_twitter.URL, media_twitter.Ideology_short))
url_recons_to_label = dict(zip(media_twitter['URL Reconstruct'], media_twitter.Ideology_short))
url_recons_redir_to_label = dict(zip(media_twitter['URL Redirect Reconstruct'], media_twitter.Ideology_short))
url_recons_path_to_label = dict(zip(media_twitter['URL Reconstruct Path'], media_twitter.Ideology_short))
url_recons_to_label['nbcnews.to'] = url_recons_to_label['nbcnews']


def get_domain_mbfc_ideo(domains):
    labels = []
    for dom in domains:
        res = '-'
        if dom in url_to_label:
            res = url_to_label[dom]
        elif dom in url_recons_to_label:
            res = url_recons_to_label[dom]
        elif dom in url_recons_redir_to_label:
            res = url_recons_redir_to_label[dom]
        elif dom in url_recons_path_to_label:
            res = url_recons_path_to_label[dom]
            
        labels.append(res)
    return labels

from utils.domain_bias_from_robertson import domain_to_allsides_categorical
def get_domain_allsides_ideo(domains):
    labels = []
    for dom in domains:
        res = '-'
        if dom in domain_to_allsides_categorical:
            res = domain_to_allsides_categorical[dom]
        labels.append(res)
    return labels