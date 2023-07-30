'''
Pre-save some files need for label spreading.

Input data:
    Data/Sec_4_2_Label_Spreading/Politician_List/country_to_id_leaning.pickle
        output by `1_country_to_seed_users.py`
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/edge_list_5.txt 
        output by `5_disparity_filer.py`

Output:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_processed/labels.pickle  
        labels of seed users
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_processed/graph.pickle
        network

Usage:
    `python Sec_4_2_Label_Spreading/6_prep_ls.py`
'''



############ replace the path below ############

seed_users_path = 'Data/Sec_4_2_Label_Spreading/Politician_List/'
retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'

############ replace the path above ############


import os
import pickle
import networkx as nx
import up
from utils.config import SELECTED_COUNTRIES



with open(f"{seed_users_path}/country_to_id_leaning.pickle", "rb") as f:
    country_to_id_leaning = pickle.load(f)


for country in SELECTED_COUNTRIES:

    seed_user_leaning = country_to_id_leaning[country]
    filepath = f"{retweet_net_path}/Country_Network/{country}/"
    
    Data = open(f"{filepath}/edge_list_5.txt", "r")


    G = nx.parse_edgelist(Data, delimiter=' ', create_using=nx.DiGraph(), nodetype=str, data=(('weight', float),))


    print("Number of nodes: ", len(G.nodes) )
    print("Number of edges: ", len(G.edges) )

    print("length seed users:", len(seed_user_leaning) )

    nodes = list(G.nodes)

    print( "overlap: ", len(  set(nodes) & set(seed_user_leaning.keys())  ) )

    labels = dict()
    nodes = list(G.nodes)
    for node in nodes:

        if node in seed_user_leaning:
            labels[node] = 'Left' if seed_user_leaning[node] == 'L' else 'Right'
        else:
            labels[node] = 'Unknown'

    print("length of labels", len(labels) )

    print("length of known labels: ", len([i for i in labels.values() if i != 'Unknown']) )

    if not os.path.exists(f"{filepath}/lp_processed"):
        os.makedirs(f"{filepath}/lp_processed")

    with open(f"{filepath}/lp_processed/labels.pickle", 'wb') as handle:
        pickle.dump(labels, handle)

    with open(f"{filepath}/lp_processed/graph.pickle", 'wb') as handle:
        pickle.dump(G, handle)
