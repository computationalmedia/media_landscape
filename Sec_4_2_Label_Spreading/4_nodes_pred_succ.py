'''
Obtain predecessors and successors of nodes in retweet network, which will be used for disparity filtering

Input data:
    Data/Sec_4_2_Label_Spreading/retweet_net_weight.csv
        output by `3_retweet_net_merge.py`
    
Output:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/node_to_succ.pickle
        nodes to their successors and edge weight
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/node_to_pred.pickle
        nodes to their predecessors and edge weight

Example usage:
    `python Sec_4_2_Label_Spreading/4_nodes_pred_succ.py`
'''


############ replace the path below ############

retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'

############ replace the path above ############

import pickle
import os
import up
from utils.config import SELECTED_COUNTRIES

for country in SELECTED_COUNTRIES:

    filepath = f"{retweet_net_path}/Country_Network/{country}/"

    with open(f"{filepath}/retweet_net_weight.csv", "r") as f:
        data = f.readlines()

    node_to_succ = dict()

    for line in data:
        node_1, node_2, w = line.strip().split()
        
        if node_1 not in node_to_succ:
            node_to_succ[node_1] = [ (node_2, int(w)) ]
        else:
            node_to_succ[node_1].append( (node_2, int(w))  )
        
    del data

    
    with open(f"{filepath}/node_to_succ.pickle", "wb") as f:
        pickle.dump(node_to_succ, f)

    del node_to_succ

    with open(f"{filepath}/retweet_net_weight.csv", "r") as f:
        data = f.readlines()

    node_to_pred = dict()


    for line in data:
        node_1, node_2, w = line.strip().split()
        
        if node_2 not in node_to_pred:
            node_to_pred[node_2] = [ (node_1, int(w)) ]
        else:
            node_to_pred[node_2].append(  (node_1, int(w))  )

    del data

    with open(f"{filepath}/node_to_pred.pickle", "wb") as f:
        pickle.dump(node_to_pred, f)

    del node_to_pred