'''
Run label spreading prediction on within-country network after including bridging users.
US is selected as an anchor country. 

Input data:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_processed/labels.pickle  
        output by `Sec_4_2_Label_Spreading/6_prep_ls.py`
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_processed/graph.pickle
        output by `Sec_4_2_Label_Spreading/6_prep_ls.py`
    Data/Sec_4_2_Label_Spreading/retweet_net_global/Bridging_Users/Edges_to_Add/{cali_country}_{anchor_country}.pickle
        output by `2_identify_bridging_users.py`

Output:
    Data/Sec_4_2_Label_Spreading/retweet_net_global/Bridging_Users/Leaning_Estimate/{cali_country}_{anchor_country}.pickle
        new estimated user leaning for a pair of countries

Usage:
    `python Sec_5_2_Bridging_Users/3_label_spreading_with_bridging_users.py`
'''


############ replace the path below ############

seed_users_path = 'Data/Sec_4_2_Label_Spreading/Politician_List/'
location_path = 'Data/Sec_4_1_Geolocation/geoparse/'
retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'

seed_users_path = '/Users/caiyang/Documents/_Honours/results/Politician_List/'
location_path = '/Users/caiyang/Documents/_Honours/user_locations/geoparse_v3/'
retweet_net_path = '/Users/caiyang/Documents/_Honours/results/Geoparsed_results/User_Retweet_with_Politician/'
retweet_net_path_save = 'Data/Sec_4_2_Label_Spreading/retweet_net/'

############ replace the path above ############


import pickle
import networkx as nx
import numpy as np
import os
import gc
import up

from scipy.sparse import diags, csr_matrix
from scipy.sparse.linalg import norm


from utils.config import SELECTED_COUNTRIES


anchor_country = 'United States'

for cali_country in SELECTED_COUNTRIES[1:]:
    
    print(f"\n country: {cali_country}\n")

    savepath = f"{retweet_net_path}/Bridging_Users/Edges_to_Add"

    with open(f"{savepath}/{cali_country}_{anchor_country}.pickle", "rb")  as handle:
        cali_anchor_edges_to_add = pickle.load(handle)

    print("cali_anchor_edges_to_add: ", len(cali_anchor_edges_to_add) )


    savepath = f"{seed_users_path}/country_to_id_leaning.pickle"
    with open(savepath, "rb") as f:
        country_to_id_leaning = pickle.load(f)
    seed_user_leaning = country_to_id_leaning[anchor_country]


    filepath = f"{retweet_net_path}/Country_Network/{anchor_country}/"

    with open(f"{filepath}/lp_processed/labels.pickle", 'rb') as handle:
        user_leanings = pickle.load(handle)

    with open(f"{filepath}/lp_processed/graph.pickle", 'rb') as handle:
        G = pickle.load(handle)


    print("before adding bridging users: ", len(G.nodes), len(G.edges))

    for (user_tweeting_id, user_tweeted_id, weight) in cali_anchor_edges_to_add:
        G.add_edge(user_tweeting_id, user_tweeted_id, weight=weight)

        if user_tweeting_id not in user_leanings:
            user_leanings[user_tweeting_id] = 'Unknown'

        if user_tweeted_id not in user_leanings:
            user_leanings[user_tweeted_id] = 'Unknown'

    print("after adding bridging users: ", len(G.nodes), len(G.edges))


    nodes = list(G.nodes)

    leaning_with_labels = [ user_leanings[user] for user in nodes if user_leanings[user] != 'Unknown' ]
    user_with_labels = [ nodes[idx] for idx, user in enumerate(nodes) if user_leanings[user] != 'Unknown' ]

    G.remove_edges_from(nx.selfloop_edges(G))

    G_und = G.to_undirected()

    sub_graphs = list( (G_und.subgraph(c) for c in nx.connected_components(G_und)) )

    del G_und
    gc.collect()

    user_with_labels_set = set(user_with_labels)

    subgraph_overlap = [ len( user_with_labels_set & set(sg.nodes) ) for sg in sub_graphs ]

    filtered_nodes = []

    for sg in sub_graphs:
        sg_nodes = list(sg.nodes)
        if len( user_with_labels_set & set(sg_nodes) ) == 0:
            filtered_nodes += sg_nodes

    G.remove_nodes_from(filtered_nodes)

    nodes = list(G.nodes)

    leaning_with_labels = [ user_leanings[user] for user in nodes if user_leanings[user] != 'Unknown' ]

    user_with_labels = [ nodes[idx] for idx, user in enumerate(nodes) if user_leanings[user] != 'Unknown' ]

    unlabeled_users = [ nodes[idx] for idx, user in enumerate(nodes) if user_leanings[user] == 'Unknown' ]

    all_users = user_with_labels + unlabeled_users

    del nodes

    alpha = 0.5
    mu = (1/alpha) - 1
    beta = mu/(1+mu)

    fold_all_users = user_with_labels  + unlabeled_users

    fold_init_labels = np.zeros(shape=(len(all_users), 2))
    print(len(fold_all_users), len(all_users))

    for i in range(len(user_with_labels)):
        leaning_idx = 0 if leaning_with_labels[i] == 'Left' else 1
        fold_init_labels[i][leaning_idx] = 1


    W_fold = nx.to_scipy_sparse_array(G, format='csr', nodelist=fold_all_users).transpose()
    W_fold += nx.to_scipy_sparse_array(G, format='csr', nodelist=fold_all_users)

    row_sum = np.sum(W_fold, 1)
    D_fold = np.power(row_sum, -0.5)
    D_fold = np.squeeze(D_fold)
    D_fold = diags(D_fold)
    S_fold = D_fold.dot(W_fold).dot(D_fold)

    fold_init_labels = csr_matrix(fold_init_labels)

    F_t = fold_init_labels.copy()

    T = 5000
    for _ in range(T) :
        F_t1 = alpha*(S_fold.dot(F_t)) + (1-alpha)*fold_init_labels
        T -= 1

        if norm(F_t1-F_t, ord='fro') <= 1e-10:
            F_t = F_t1
            break
        F_t = F_t1

    pred_results = []
    test_user_with_labels = dict()

    for i in range(len(user_with_labels), len(fold_all_users)):
        if F_t[i, 0] == F_t[i, 1] and F_t[i, 0] == 0:
            pred_results.append(i)
            continue

        user_id = fold_all_users[i]
        test_user_with_labels[user_id] = F_t[i, 1]/F_t[i].sum()
        if np.isnan( F_t[i, 1]/F_t[i].sum() ):
            print(f"found nan: {i}" )


    uid_to_leaning = dict()
    for user_id in user_with_labels:
        score = 1 if user_leanings[user_id] == 'Right' else 0
        uid_to_leaning[user_id] = score

    for user_id, leaning_score in test_user_with_labels.items():
        uid_to_leaning[user_id] = leaning_score

    filepath = f'{retweet_net_path_save}/Bridging_Users/Leaning_Estimate'
    if not os.path.exists(filepath):
        os.makedirs(filepath)
        
    with open(f"{filepath}/{cali_country}_{anchor_country}.pickle", 'wb') as handle:
        pickle.dump(uid_to_leaning, handle)
        