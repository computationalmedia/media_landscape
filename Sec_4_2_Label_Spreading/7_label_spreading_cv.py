'''
Label spreading with cross validation. Also can be used to tune the hyperparameters.
It runs for a given country only.

Input data:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_processed/labels.pickle  
        output by `6_prep_ls.py`
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/lp_processed/graph.pickle
        output by `6_prep_ls.py`
        
Output:
    Cross validation performance
    
Usage:
    `python3 Sec_4_2_Label_Spreading/7_label_spreading_cv.py`
'''




############ replace the path below ############

retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'
COUNTRY = 'United States'

############ replace the path above ############


import pickle
import networkx as nx
import numpy as np
import gc
import up

from sklearn.model_selection import StratifiedKFold
from scipy.sparse import diags, csr_matrix
from scipy.sparse.linalg import norm
from operator import itemgetter
from sklearn.metrics import classification_report

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
print("after removing: ", len(G.nodes))


nodes = list(G.nodes)

leaning_with_labels = [ user_leanings[user] for user in nodes if user_leanings[user] != 'Unknown' ]

user_with_labels = [ nodes[idx] for idx, user in enumerate(nodes) if user_leanings[user] != 'Unknown' ]
unlabeled_users = [ nodes[idx] for idx, user in enumerate(nodes) if user_leanings[user] == 'Unknown' ]

all_users = user_with_labels + unlabeled_users

print("user_with_labels: ", len(user_with_labels))
print('len(all_users):', len(all_users))

del nodes



skf = StratifiedKFold(n_splits=10, random_state=None, shuffle=False)

alpha = country_to_alpha[COUNTRY]
mu = (1/alpha) - 1
beta = mu/(1+mu)

pred_results = []
true_labels = []
users_with_ties = []
users_with_ties_labels = []
users_with_wrong_pred = []

for train_index, test_index in skf.split(user_with_labels, leaning_with_labels):
    
    fold_train_labeled_users = list(itemgetter(*train_index)(user_with_labels))
    fold_train_labeled_labels = list(itemgetter(*train_index)(leaning_with_labels))
    
    fold_test_labeled_users = list(itemgetter(*test_index)(user_with_labels))
    fold_test_labeled_labels = list(itemgetter(*test_index)(leaning_with_labels))
        
    fold_all_users = fold_train_labeled_users + fold_test_labeled_users + unlabeled_users
    
    fold_init_labels = np.zeros(shape=(len(fold_all_users), 2))
    print(len(fold_all_users), len(all_users))
    
    for i in range(len(fold_train_labeled_labels)):
        leaning_idx = 0 if fold_train_labeled_labels[i] == 'Left' else 1
        fold_init_labels[i][leaning_idx] = 1

    fold_init_labels = csr_matrix(fold_init_labels)
    
    W_fold = nx.to_scipy_sparse_array(G, format='csr', nodelist=fold_all_users).transpose()
    W_fold += nx.to_scipy_sparse_array(G, format='csr', nodelist=fold_all_users)
    
    row_sum = np.sum(W_fold, 1)
    D_fold = np.power(row_sum, -0.5)
    del row_sum
    D_fold = np.squeeze(D_fold)
    D_fold = diags(D_fold)
    S_fold = D_fold.dot(W_fold).dot(D_fold)
    del W_fold, D_fold
            
    F_t = fold_init_labels.copy()

    T = 5000
    for _ in range(T) :
        F_t1 = alpha*(S_fold@F_t) + (1-alpha)*fold_init_labels 
        T -= 1
        
        if norm(F_t1-F_t, ord='fro') <= 1e-10:
            F_t = F_t1
            break
        F_t = F_t1
    
    del S_fold
    print( f"After iterations: { norm(F_t1-F_t, ord='fro')}")
        
    fold_pred_results = []

    for i in range(len(fold_train_labeled_users), len(leaning_with_labels)):
            
        fold_pred_results.append(np.argmax(F_t[i]))
        
    pred_results += fold_pred_results
            
    for i in range(len(fold_test_labeled_labels)):
        
        true_labels.append(fold_test_labeled_labels[i])

    
left = 0
right = 0
counter = 0
label_to_int = {0: 'Left', 1: 'Right'}
pred_results_str = [label_to_int[i] for i in pred_results]
for i in range(len(pred_results_str)):
    if pred_results_str[i] == true_labels[i]:
        if pred_results_str[i] == 'Left' and true_labels[i] == 'Left':
            left += 1
        elif pred_results_str[i] == 'Right' and true_labels[i] == 'Right':
            right += 1
        counter += 1

print('acc:', float(counter)/len(true_labels))
print('left acc:', float(left)/len([a for a in leaning_with_labels if a == 'Left']))
print('right acc:', float(right)/len([a for a in leaning_with_labels if a == 'Right']))
print(len([a for a in leaning_with_labels if a == 'Left']))
print(len([a for a in leaning_with_labels if a == 'Right']))

print(classification_report(true_labels, pred_results_str, digits=4))