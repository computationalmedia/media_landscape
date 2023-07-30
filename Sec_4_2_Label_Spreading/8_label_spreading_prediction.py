'''
Label spreading for predicting politicial leaning of users
It runs for a given country only.

Input data:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_processed/labels.pickle  
        output by `6_prep_ls.py`
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_processed/graph.pickle
        output by `6_prep_ls.py`
        
Output:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_prediction/uid_to_leaning_lp.pickle
        cross validation performance

Usage:
    `python3 Sec_4_2_Label_Spreading/8_label_spreading_prediction.py`
    
'''




############ replace the path below ############

retweet_net_path = 'retweet_net/'
COUNTRY = 'United States'

############ replace the path above ############


import pickle
import networkx as nx
import numpy as np
import os
import up

from scipy.sparse import diags, csr_matrix
from scipy.sparse.linalg import norm


from utils.config import SELECTED_COUNTRIES

alphas = [0.5, 0.5, 0.25, 0.55, 0.3, 0.8, 0.05, 0.05]
country_to_alpha = dict(zip(SELECTED_COUNTRIES, alphas))


filepath = f"{retweet_net_path}/Country_Network/{COUNTRY}/"

with open(f"{filepath}/lp_processed/labels.pickle", 'rb') as handle:
    user_leanings = pickle.load(handle)
    
with open(f"{filepath}/lp_processed/graph.pickle", 'rb') as handle:
    G = pickle.load(handle)


nodes = list(G.nodes)
user_with_labels = [ nodes[idx] for idx, user in enumerate(nodes) if user_leanings[user] != 'Unknown' ]


G_und = G.to_undirected()

sub_graphs = list( (G_und.subgraph(c) for c in nx.connected_components(G_und)) )

del G_und


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
print("after removing: ", len(G.nodes))


print("\nbefore removing: ", len(G.edges))
G.remove_edges_from(nx.selfloop_edges(G))
print('after removing self-loop edges: ', len(G.edges) )


nodes = list(G.nodes)

leaning_with_labels = [ user_leanings[user] for user in nodes if user_leanings[user] != 'Unknown' ]

user_with_labels = [ nodes[idx] for idx, user in enumerate(nodes) if user_leanings[user] != 'Unknown' ]

unlabeled_users = [ nodes[idx] for idx, user in enumerate(nodes) if user_leanings[user] == 'Unknown' ]

all_users = user_with_labels + unlabeled_users

print("user_with_labels: ", len(user_with_labels))
print('len(all_users):', len(all_users))


alpha = country_to_alpha[COUNTRY]
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
        
print( len(pred_results) )
print( len(test_user_with_labels) )


uid_to_leaning = dict()
for user_id in user_with_labels:
    score = 1 if user_leanings[user_id] == 'Right' else 0
    uid_to_leaning[user_id] = score
    
for user_id, leaning_score in test_user_with_labels.items():
    uid_to_leaning[user_id] = leaning_score
    
    
left_cnt = len( [ uid for uid, leaning in uid_to_leaning.items() if leaning <= 0.5 ] )
right_cnt = len( [ uid for uid, leaning in uid_to_leaning.items() if leaning > 0.5 ] )

print(left_cnt, right_cnt, left_cnt/right_cnt)


if not os.path.exists(f"{filepath}/lp_prediction"):
    os.makedirs(f"{filepath}/lp_prediction")
        
with open(f"{filepath}/lp_prediction/uid_to_leaning_lp.pickle", 'wb') as handle:
    pickle.dump(uid_to_leaning, handle)