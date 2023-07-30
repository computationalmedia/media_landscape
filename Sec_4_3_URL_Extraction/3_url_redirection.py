'''
Perform redirection on those URLs from shortened domains

Input data:
    Data/Sec_4_3_URL_Extraction/URLs/urls_to_redirect.pickle
        output by `2_gather_redirected_urls.py`
    
Output (within the given directory):
    urls_redirected.pickle

Usage:
    `python Sec_4_3_URL_Extraction/3_url_redirectionn.py `
    
'''

############ replace the path below ############

data_path='Data/Sec_4_3_URL_Extraction/URLs/urls_to_redirect.pickle'
opt_path='Data/Sec_4_3_URL_Extraction/URLs/'
num_processes=16

############ replace the path above ############



import pickle
import requests
import numpy as np
import os
from multiprocessing import Process, Manager

def URL_list_redirect(urls, process_num, return_dict):
    urls_redirected = {}
    success_cnt = 0
    
    for idx, original_link in enumerate(urls):
        redirected_url = None
        try:
            r = requests.head(original_link, allow_redirects=True, timeout=1, verify=False)
            redirected_url = r.url.strip()
            urls_redirected[original_link] = redirected_url
            if redirected_url != '':
                success_cnt += 1
        except:
            urls_redirected[original_link] = ''

        if (idx+1) % 1000 == 0:
            print(f"{process_num} - {idx+1} - {success_cnt}/{idx+1} - { success_cnt/(idx+1) }")

    return_dict[process_num] = ( urls_redirected, success_cnt )
    return return_dict

def URL_redirect_parallel(urls, num_processes, savepath):
    manager = Manager()
    return_dict = manager.dict()

    processes = []

    avg = int( np.ceil( len(urls) / num_processes ) )
    last = 0
    
    for w in range(num_processes):
        if last < len(urls):
            p = Process( target=URL_list_redirect, args=(urls[ last: last+avg ], w, return_dict) )

            p.daemon = True
            p.start()
            processes.append(p)

            last += avg 

    for proc in processes:
        proc.join()

    url_to_redirection = {}
    total_success_cnt = 0
    for data, success_cnt in return_dict.values():
        for url, url_redir in data.items():
            url_to_redirection[url] = url_redir

        total_success_cnt += success_cnt

    print(f"total_success_cnt: {total_success_cnt}; given: {len(urls)}")
    print(f"total_success_cnt ratio: {total_success_cnt/len(urls)}")

    with open(f"{savepath}/urls_redirected.pickle", "wb") as f:
        pickle.dump(url_to_redirection, f)
    

if __name__ == "__main__":

    if not os.path.isdir(opt_path):
        os.makedirs(opt_path)

    with open(data_path, "rb") as f:
        urls_to_redirect = pickle.load(f)

    URL_redirect_parallel(urls_to_redirect, num_processes, opt_path)