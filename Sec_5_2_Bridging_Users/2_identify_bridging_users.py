'''
Find the set of bridging users, i.e. users from one country retweeting people in a different country.

Input data:
    Data/Sec_4_1_Geolocation/geoparse/merged_uid_to_world_loc_w_pol.pickle
        output by `Sec_4_1_Geolocation/7_add_politicians_to_geolocation.py`
    Data/Sec_4_2_Label_Spreading/Politician_List/country_to_id_leaning.pickle
        output by `Sec_4_2_Label_Spreading/1_country_to_seed_users.py`
    Data/Sec_4_2_Label_Spreading/retweet_net_global/lp_processed/labels.pickle  
        see `1.5_retweet_net_process`
    Data/Sec_4_2_Label_Spreading/retweet_net_global/lp_processed/graph.pickle
        see `1.5_retweet_net_process`
        
Output:
    Data/Sec_4_2_Label_Spreading/retweet_net_global/Bridging_Users/Edges_to_Add/{cali_country}_{anchor_country}.pickle
        for country to calibrate and a given anchor country 
        
Usage:
    `python Sec_5_2_Bridging_Users/2_identify_bridging_users.py`
'''

############ replace the path below ############

seed_users_path = 'Data/Sec_4_2_Label_Spreading/Politician_List/'
location_path = 'Data/Sec_4_1_Geolocation/geoparse/'
retweet_net_global_path = 'Data/Sec_4_2_Label_Spreading/retweet_net_global/'
retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'

seed_users_path = '/Users/caiyang/Documents/_Honours/results/Politician_List/'
location_path = '/Users/caiyang/Documents/_Honours/user_locations/geoparse_v3/'
retweet_net_global_path = '/Users/caiyang/Documents/_Honours/results/Geoparsed_results/User_Retweet_with_Politician_Global/'
retweet_net_path = '/Users/caiyang/Documents/_Honours/results/Geoparsed_results/User_Retweet_with_Politician/'
retweet_net_path_save = 'Data/Sec_4_2_Label_Spreading/retweet_net/'

############ replace the path above ############


import pickle
import gc
import os
import up
import networkx as nx

from utils.config import SELECTED_COUNTRIES

path = f"{location_path}/merged_uid_to_world_loc_w_pol.pickle"
with open(path, "rb") as f:
    users_to_unq_loc = pickle.load(f)


savepath = f"{seed_users_path}/country_to_id_leaning.pickle"
with open(savepath, "rb") as f:
    country_to_id_leaning = pickle.load(f)


filepath = f"{retweet_net_global_path}/Network/"
with open(f"{filepath}/lp_processed/labels.pickle", 'rb') as handle:
    user_leanings = pickle.load(handle)
    
with open(f"{filepath}/lp_processed/graph.pickle", 'rb') as handle:
    G = pickle.load(handle)


nodes = list(G.nodes)

leaning_with_labels = [ user_leanings[user] for user in nodes if user_leanings[user] != 'Unknown' ]
user_with_labels = [ nodes[idx] for idx, user in enumerate(nodes) if user_leanings[user] != 'Unknown' ]

print("before removing: ", len(G.edges))
G.remove_edges_from(nx.selfloop_edges(G))
print('after removing self-loop edges: ', len(G.edges) )


G_und = G.to_undirected()

sub_graphs = list( (G_und.subgraph(c) for c in nx.connected_components(G_und)) )

del G_und
gc.collect()

print(f"There are {len(sub_graphs)} sub graphs")

user_with_labels_set = set(user_with_labels)

subgraph_overlap = [ len( user_with_labels_set & set(sg.nodes) ) for sg in sub_graphs ]

print('How many contains seed users: ', len([i for i in subgraph_overlap if i > 0]) )
print("before removing: ", len(G.nodes))

filtered_nodes = []

for sg in sub_graphs:
    sg_nodes = list(sg.nodes)
    if len( user_with_labels_set & set(sg_nodes) ) == 0:
        filtered_nodes += sg_nodes

G.remove_nodes_from(filtered_nodes)
        
print("after removing nodes: ", len(G.nodes))
print("after removing edges: ", len(G.edges))



anchor_bridge_retweets = {c: { i: set() for i in SELECTED_COUNTRIES } for c in SELECTED_COUNTRIES}

for edge_weight in G.edges.data():
    user_tweeting_id, user_tweeted_id = edge_weight[0], edge_weight[1]
    weight = int( edge_weight[-1]['weight'] )

    tweeting_loc = users_to_unq_loc[ user_tweeting_id.strip() ]
    tweeted_loc = users_to_unq_loc[ user_tweeted_id.strip() ]
    
    if tweeting_loc == tweeted_loc:
        continue
        
    anchor_bridge_retweets[tweeting_loc][tweeted_loc].add( (user_tweeting_id, user_tweeted_id) )


cali_country_to_anchor_country = {c: { i: 0 for i in SELECTED_COUNTRIES } for c in SELECTED_COUNTRIES}

for cali_country in SELECTED_COUNTRIES:
    for anchor_country in SELECTED_COUNTRIES:
        if cali_country == anchor_country:
            continue
        
        cali_to_anchor = anchor_bridge_retweets[cali_country][anchor_country]
        
        filepath = f"{retweet_net_path}/Country_Network/{cali_country}/"
        with open(f"{filepath}/lp_prediction/uid_to_leaning_lp.pickle", 'rb') as handle:
            cali_uid_to_leaning = pickle.load(handle)
        cali_uids = set(cali_uid_to_leaning.keys())
            
        filepath = f"{retweet_net_path}/Country_Network/{anchor_country}/"
        with open(f"{filepath}/lp_prediction/uid_to_leaning_lp.pickle", 'rb') as handle:
            anchor_uid_to_leaning = pickle.load(handle)
        anchor_uids = set(anchor_uid_to_leaning.keys())
        
        qualified = set()
        for (tweeting_id, tweeted_id) in cali_to_anchor:
            if tweeting_id not in cali_uids: # or tweeted_id not in anchor_uids:
                continue
            qualified.add( tweeting_id )
        
        cali_country_to_anchor_country[cali_country][anchor_country] = qualified



for cali_country in SELECTED_COUNTRIES:
    for anchor_country in SELECTED_COUNTRIES:
        if cali_country == anchor_country:
            continue

        cali_anchor_users = cali_country_to_anchor_country[cali_country][anchor_country]

        cali_anchor_edges_to_add = set()

        for edge_weight in G.edges.data():
            user_tweeting_id, user_tweeted_id = edge_weight[0], edge_weight[1]
            weight = int( edge_weight[-1]['weight'] )

            tweeting_loc = users_to_unq_loc[ user_tweeting_id.strip() ]
            tweeted_loc = users_to_unq_loc[ user_tweeted_id.strip() ]

            if not (user_tweeting_id in cali_anchor_users ):
                continue

            if user_tweeted_id in cali_anchor_users or tweeted_loc == anchor_country :  
                # retweets between cali users OR retweets between cali user and anchor user

                cali_anchor_edges_to_add.add( (user_tweeting_id, user_tweeted_id, weight) )
                
                
        if not os.path.exists(f"{retweet_net_path_save}/Bridging_Users/Edges_to_Add"):
            os.makedirs(f"{retweet_net_path_save}/Bridging_Users/Edges_to_Add")
            
        savepath = f"{retweet_net_path_save}/Bridging_Users/Edges_to_Add"
        
        with open(f"{savepath}/{cali_country}_{anchor_country}.pickle", "wb")  as handle:
            pickle.dump(cali_anchor_edges_to_add, handle)
        
        