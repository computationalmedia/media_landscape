'''
Disparity filtering on retweet network to extract backbone network. 
Adapted from https://github.com/aekpalakorn/python-backbone-network/blob/master/backbone.py

Input data:
    Data/Sec_4_2_Label_Spreading/Politician_List/country_to_id_leaning.pickle
        output by `1_country_to_seed_users.py`
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/node_to_succ.pickle
        output by `4_nodes_pred_succ.py`
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/node_to_pred.pickle
        nodes by `4_nodes_pred_succ.py`

Output data:
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/graph_disp_info.txt
        immediate information
    Data/Sec_4_2_Label_Spreading/retweet_net/Country_Network/{country}/edge_list_5.txt 
        backbone network, this is what we need for label spreading later
        
Usage:
    `python Sec_4_2_Label_Spreading/5_disparity_filter.py`
'''


############ replace the path below ############

seed_users_path = 'Data/Sec_4_2_Label_Spreading/Politician_List/'
retweet_net_path = 'Data/Sec_4_2_Label_Spreading/retweet_net/'

############ replace the path above ############


import pickle
import gc
import up
from scipy import integrate

from utils.config import SELECTED_COUNTRIES

def disparity_filter(G, node_to_succ, node_to_pred, file_to_write):
    ''' Compute significance scores (alpha) for weighted edges in G as defined in Serrano et al. 2009
        Args
            G: Weighted NetworkX graph
        Returns
            Weighted graph with a significance score (alpha) assigned to each edge
        References
            M. A. Serrano et al. (2009) Extracting the Multiscale backbone of complex weighted networks. PNAS, 106:16, pp. 6483-6488.
    '''
        
    with open(file_to_write, "w") as f:

        for u in G:
            u_out = node_to_succ[u] if u in node_to_succ else []
            k_out = len( u_out  )
            u_in = node_to_pred[u] if u in node_to_pred else []
            k_in = len( u_in  )

            line_to_write = ""

            if k_out > 1:
                sum_w_out = sum( [p[1] for p in u_out] ) 
                for v, w in u_out:
                    p_ij_out = w/sum_w_out
                    alpha_ij_out = 1 - (k_out-1) * integrate.quad(lambda x: (1-x)**(k_out-2), 0, p_ij_out)[0]

                    line_to_write = f"{u} {v} {w} {float('%.4f' % alpha_ij_out)} {None}"
                    f.write(line_to_write+"\n")
        
            elif k_out == 1 and u_out[0][0] in node_to_pred and len( node_to_pred[ u_out[0][0] ] ) == 1:
                #we need to keep the connection as it is the only way to maintain the connectivity of the network
                v = u_out[0][0]
                w = u_out[0][1]

                #there is no need to do the same for the k_in, since the link is built already from the tail
                line_to_write = f"{u} {v} {w} {0} {0}"
                f.write(line_to_write+"\n")

            if k_in > 1:
                sum_w_in = sum( [p[1] for p in u_in] ) 
                for v, w in u_in:
                    p_ij_in = w/sum_w_in
                    alpha_ij_in = 1 - (k_in-1) * integrate.quad(lambda x: (1-x)**(k_in-2), 0, p_ij_in)[0]

                    line_to_write = f"{v} {u} {w} {None} {float('%.4f' % alpha_ij_in)}"
                    f.write(line_to_write+"\n")

    print("Done")


def write_graph_csv(savepath, N, alpha_t=0.4, cut_mode='or', seed_users=None):

    with open(savepath, 'w') as f:

        for line in N:

            u, v, w, alpha_out, alpha_in = line.split()
            w = float(w)

            alpha_in = 1 if alpha_in == 'None' else float(alpha_in)
            alpha_out = 1 if alpha_out == 'None' else float(alpha_out)
            
            if cut_mode == 'or':
                if alpha_in<alpha_t or alpha_out<alpha_t or str(u) in seed_users or str(v) in seed_users:
                    f.write(f"{u} {v} {w}\n")

            elif cut_mode == 'and':
                if alpha_in<alpha_t and alpha_out<alpha_t:
                    f.write(f"{u} {v} {w}\n")
        

            
if __name__ == '__main__':
    
    for country in SELECTED_COUNTRIES:
        
        filepath = f"{retweet_net_path}/Country_Network/{country}/"

        with open(f"{filepath}/retweet_net_weight.csv", "r") as f:
            data = f.readlines()

        nodes = set()
        for line in data:
            n1, n2, _ = line.split()
            nodes.add(n1)
            nodes.add(n2)
        del data
        gc.collect()

        with open(f"{filepath}/node_to_succ.pickle", "rb") as f:
            node_to_succ = pickle.load(f)

        print('loading node_to_succ done')

        with open(f"{filepath}/node_to_pred.pickle", "rb") as f:
            node_to_pred = pickle.load(f)

        print('loading node_to_pred done')

        disparity_filter(nodes, node_to_succ, node_to_pred, f"{filepath}/graph_disp_info.txt")
    
        del nodes, node_to_succ, node_to_pred


        with open(f"{seed_users_path}/country_to_id_leaning.pickle", "rb") as f:
            country_to_id_leaning = pickle.load(f)

        country_politicians = country_to_id_leaning[country]
        seed_users = set( country_politicians.keys() )

        alpha = 0.05
        with open( f'{filepath}/graph_disp_info.txt', 'r' ) as f:
            graph_disp_info = f.readlines()
            graph_disp_info = [line for line in graph_disp_info if line.strip() != ""]

        savepath = f"{filepath}/edge_list_5.txt"
        write_graph_csv( savepath, graph_disp_info, alpha_t=alpha, cut_mode='or', seed_users=seed_users)
        del graph_disp_info
