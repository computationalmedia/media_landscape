'''
Domain bias scores for US users.
It covers Roberson et al Bias Score, Facebook Bias Score, MTurk Bias Score, Budak et al Bias Score, 
AllSides Patented Bias Score and Pew Bias Score
          
Part of them come from 
    Ronald E Robertson, Shan Jiang, Kenneth Joseph, Lisa Friedland, David Lazer, and Christo Wilson. 2018. 
    Auditing Partisan Audience Bias within Google Search. 
    Proceedings of the ACM on Human-Computer Interaction CSCW (2018)
'''


import numpy as np
import pandas as pd
import pickle

###### Pew Research Bias Scores ######

pew_audience_size = {
    'abcnews.go.com': [0.14, 0.23, 0.41, 0.15, 0.06],
    'nytimes.com': [0.40, 0.25, 0.23, 0.09, 0.03],
    'washingtonpost.com': [0.34, 0.27, 0.20, 0.12, 0.07], 
    'huffingtonpost.com': [0.34, 0.25, 0.23, 0.11, 0.06], 
    'cnn.com': [0.19, 0.25, 0.40, 0.12, 0.04],
    'buzzfeed.com': [0.32, 0.27, 0.27, 0.13, 0.01], 
    'npr.org': [0.46, 0.21, 0.26, 0.09, 0.03], 
    'wsj.com': [0.20, 0.21, 0.24, 0.22, 0.13], 
    'usatoday.com': [0.17, 0.24, 0.32, 0.19, 0.08], 
    'theguardian.com': [0.46, 0.26, 0.20, 0.07, 0.02], 
    'nbcnews.com': [0.16, 0.26, 0.39, 0.14, 0.05], 
    'bloomberg.com': [0.20, 0.23, 0.28, 0.19, 0.10], 
    'politico.com': [0.44, 0.15, 0.16, 0.15, 0.09], 
    'slate.com': [0.55, 0.21, 0.14, 0.10, 0.00], 
    'foxnews.com': [0.04, 0.14, 0.37, 0.27, 0.19],
    'cbsnews.com': [0.16, 0.24, 0.39, 0.16, 0.06], 
    'yahoo.com': [0.11, 0.24, 0.41, 0.18, 0.06], 
     'newyorker.com': [0.52, 0.25, 0.16, 0.06, 0.00], 
    'economist.com': [0.35, 0.24, 0.23, 0.14, 0.05],
    'pbs.org': [0.35, 0.25, 0.26, 0.11, 0.04], 
    'bbc.com': [0.32, 0.28, 0.26, 0.08, 0.05], 
    'thecolbertreport.cc.com': [0.41, 0.27, 0.22, 0.09, 0.01],  
    'msnbc.com': [0.22, 0.33, 0.33, 0.14, 0.04], 
    'theblaze.com': [0.04, 0.03, 0.08, 0.34, 0.51], 
    'hannity.com': [0.03, 0.01, 0.13, 0.39, 0.45],
    'aljazeera.america.com': [0.43, 0.28, 0.19, 0.05, 0.05],
    'google.news.com': [0.13, 0.24, 0.43, 0.15, 0.05],
    'glennbeck.com': [0.02, 0.01, 0.10, 0.37, 0.49],
    'rushlimbaugh.com': [0.02, 0.01, 0.14, 0.37, 0.46],
    'drudgereport.com': [0.04, 0.04, 0.18, 0.38, 0.36],
    'breitbart.com': [0.03, 0.04, 0.14, 0.31, 0.48]
}

domain_to_pew = {}

for domain, aud_size in pew_audience_size.items():
    aud_size_arr = np.array(aud_size)
    domain_to_pew[domain] = (aud_size_arr*np.array([-1, -0.5, 0, 0.5, 1]) ).sum()
    
    
    
    
###### All Sides Scores ######

# Joint scores of robertson's AllSides scores and our scraped AllSides scores

bias_score_path = "Data/Sec_5_3_Media_Domain_Bias/bias_score_v2.csv"
rob_domain = pd.read_csv(bias_score_path)

bias_score_path = "Data/Sec_5_3_Media_Domain_Bias/bias_scores.csv"
rob_v1 = pd.read_csv(bias_score_path)

domain_to_allsides = dict(zip( rob_v1.domain, rob_v1.allsides_score ) )

rob_domain['allsides_score'] = rob_domain.domain.apply(lambda x: domain_to_allsides[x])

domain_to_allsides = dict(zip( rob_domain.domain_reconstruct, rob_domain.allsides_score ) )
domain_to_allsides = {domain: score for domain, score in domain_to_allsides.items() if not np.isnan(score) }




with open(f"Data/Sec_5_3_Media_Domain_Bias/allsides_media_to_bias.pickle", "rb") as f:
    media_to_bias = pickle.load(f)
    
media_to_bias_update = {}

for media, bias in media_to_bias.items():
    media_to_bias_update[media] = bias
    
    if "(Online)" in media:
        media_ = media.replace("(Online)", "").strip()
        media_to_bias_update[media_] = bias
    if "(Online News)" in media:
        media_ = media.replace("(Online News)", "").strip()
        media_to_bias_update[media_] = bias
    if media.endswith('News'):
        media_ = media[:-4].strip()
        media_to_bias_update[media_] = bias
    
print(f"{len(media_to_bias)} --> {len(media_to_bias_update)}")
media_to_bias = media_to_bias_update.copy()


media_twitter_path = 'Data/Sec_5_3_Media_Domain_Bias/media_twitter_collections_with_bias.csv'

media_twitter = pd.read_csv(media_twitter_path)
media_twitter = media_twitter[ (media_twitter['Parent Country'] != 'Unknown') ]

# manual change nextnewsnetwork channel on youtube
media_twitter.loc[media_twitter.URL.str.contains('youtube'), 'URL Reconstruct'] = 'nextnewsnetwork'
media_twitter.loc[media_twitter.URL.str.contains('youtube'), 'URL Redirect Reconstruct'] = 'nextnewsnetwork'


allsides_w_names = set( media_twitter.Title.str.lower().values ) & set( [ i.lower() for i in media_to_bias.keys() ] )

media_to_bias_lower = { k.lower() : v for k, v in media_to_bias.items() }

mbfc_title_to_domain_1 = dict( zip( media_twitter.Title.str.lower().values, media_twitter['URL Reconstruct'] ))
mbfc_title_to_domain_2 = dict( zip( media_twitter.Title.str.lower().values, media_twitter['URL Reconstruct Path'] ))

robertson_domains = rob_domain.domain_reconstruct.unique()

allsides_domain_to_label = {}
allsides_label_mapping = {'Center': 'C', 'Lean Left': 'CL', 'Lean Right': 'CR', 'Left': 'L', 'Right': 'R'}

for name in allsides_w_names:
    
    domain_givenby_mbfc_1 = mbfc_title_to_domain_1[name]
    domain_givenby_mbfc_2 = mbfc_title_to_domain_2[name]
    
    label = media_to_bias_lower[name]
    
    if label == 'Mixed':
        continue
    
    if domain_givenby_mbfc_1 == domain_givenby_mbfc_2 and domain_givenby_mbfc_1 in robertson_domains:
        
        if '.org' in domain_givenby_mbfc_1:
            domain_givenby_mbfc_1 = domain_givenby_mbfc_1.replace(".org", "")
        if '.online' in domain_givenby_mbfc_1:
            domain_givenby_mbfc_1 = domain_givenby_mbfc_1.replace(".online", "")

        allsides_domain_to_label[domain_givenby_mbfc_1] = allsides_label_mapping[label]
        
        
domain_to_allsides_upt = {}
for domain, allsides_bias in domain_to_allsides.items():
    bias_label = {-1: 'L', -0.5: 'CL', 0: 'C', 0.5: 'CR', 1: 'R'}[allsides_bias]
    domain_to_allsides_upt[domain] = bias_label
    if '.org' in domain:
        domain_ = domain.replace(".org", "")
        domain_to_allsides_upt[domain_] = bias_label
    if '.online' in domain:
        domain_ = domain.replace(".online", "")
        domain_to_allsides_upt[domain_] = bias_label
        
domain_to_allsides = domain_to_allsides_upt.copy()     
domain_to_allsides.update(allsides_domain_to_label)

domain_to_allsides_categorical = domain_to_allsides.copy()

bias_score_path = "Data/Sec_5_3_Media_Domain_Bias/bias_score_v2.csv"
rob_domain = pd.read_csv(bias_score_path)

domain_to_rob = dict(zip( rob_domain.domain_reconstruct, rob_domain.score ) )

bias_score_path = "Data/Sec_5_3_Media_Domain_Bias/bias_scores.csv"
rob_v1 = pd.read_csv(bias_score_path)

domain_to_fb = dict(zip( rob_v1.domain, rob_v1.fb_score ) )
domain_to_mturk = dict(zip( rob_v1.domain, rob_v1.mturk_score ) )
domain_to_budak = dict(zip( rob_v1.domain, rob_v1.budak_score ) )

# domain_to_pew = dict(zip( rob_v1.domain, rob_v1.pew_score ) )
bias_label = {'L': -1, 'CL': -0.5, 'C': 0, 'CR': 0.5, 'R': 1}

rob_domain['fb_score'] = rob_domain.domain.apply(lambda x: domain_to_fb[x])
rob_domain['mturk_score'] = rob_domain.domain.apply(lambda x: domain_to_mturk[x])
rob_domain['budak_score'] = rob_domain.domain.apply(lambda x: domain_to_budak[x])
rob_domain['allsides_score'] = rob_domain.domain_reconstruct.apply(lambda x: bias_label[ domain_to_allsides[x] ] \
                                                    if x in domain_to_allsides else np.nan)
rob_domain['pew_score'] = rob_domain.domain.apply(lambda x: domain_to_pew[x] if x in domain_to_pew else None)

domain_to_fb = dict(zip( rob_domain.domain_reconstruct, rob_domain.fb_score ) )
domain_to_fb = {domain: score for domain, score in domain_to_fb.items()  if not np.isnan(score) }

domain_to_mturk = dict(zip( rob_domain.domain_reconstruct, rob_domain.mturk_score ) )
domain_to_mturk = {domain: score for domain, score in domain_to_mturk.items() if not np.isnan(score) }

domain_to_budak = dict(zip( rob_domain.domain_reconstruct, rob_domain.budak_score ) )
domain_to_budak = {domain: score for domain, score in domain_to_budak.items() if not np.isnan(score) }

domain_to_allsides = dict(zip( rob_domain.domain_reconstruct, rob_domain.allsides_score ) )
domain_to_allsides = {domain: score for domain, score in domain_to_allsides.items() if not np.isnan(score) }

domain_to_pew = dict(zip( rob_domain.domain_reconstruct, rob_domain.pew_score ) )
domain_to_pew = {domain: score for domain, score in domain_to_pew.items() if not np.isnan(score) }