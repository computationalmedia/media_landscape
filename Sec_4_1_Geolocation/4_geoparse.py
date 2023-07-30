'''
Parse Twitter users' location using multiprocessing

Input data:
    Data/Sec_4_1_Geolocation/user_locations/merged_unique_locations.pickle
        output by `3_location_process.py`
    Data/Sec_4_1_Geolocation/stateName_to_stateAbbrv.json
    Data/Sec_4_1_Geolocation/worldcities.csv
        from simplemaps
    
Output:
    Data/Sec_4_1_Geolocation/geoparse/unique_loc_parsed_country.pickle 
    Data/Sec_4_1_Geolocation/geoparse/unique_loc_parsed_states.pickle 
    Data/Sec_4_1_Geolocation/geoparse/problematic_loc_parsed.pickle (by-product)
    
Example usage:
    `python Sec_4_1_Geolocation/3_geoparse.py`

'''



############ replace the path below ############

unique_locations_path = 'Data/Sec_4_1_Geolocation/user_locations/merged_unique_locations.pickle'
opt_dir = 'Data/Sec_4_1_Geolocation/geoparse/'
nproc = 16

############ replace the path above ############

import os
import numpy as np 
import time, pickle
from multiprocessing import Process, Manager
from parser import Parser


def chunkIt(seq, num):
    print(type(seq))
    if type(seq) is not list:
        seq = list(seq)
        
    avg = np.ceil(len(seq) / float(num))
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

def parse_location(unique_locations_path, city_path, proc_num, opt_dir, return_dict):

    geoparser = Parser()
    geoparser.load_data(city_path)

    with open(unique_locations_path, 'rb') as handle:
        unique_locations = set(pickle.load(handle))

    description_to_multi_loc = {}

    loc_to_country = {}
    loc_to_state = {}

    for i, loc in enumerate(unique_locations):

        if (i+1) % 20000 == 0:
            print(f'process {proc_num} parsed {i+1} so far')

        if loc is None or len(loc) <=1 or len(loc) > 5000 or loc.isdigit():
            continue

        loc_trans = loc
        possible_countries, corresponding_admins = geoparser.parse_location(loc_trans)

        if len(possible_countries) == 1:
            loc_to_country[loc] = list(possible_countries)[0]
            if 'United States' in possible_countries:
                if len(corresponding_admins) == 1:
                    loc_to_state[loc] = list(corresponding_admins)[0]
        
        elif len(possible_countries) > 1:
            description_to_multi_loc[loc] = possible_countries

    print(f"process {proc_num} parsed {len(loc_to_country)} locations using rule-based methods in total.")
    print(f"process {proc_num} parsed {len(loc_to_state)} US states using rule-based methods in total.")

    savepath = opt_dir+'unique_loc_{}_country_rule.pickle'.format(proc_num)
    with open(savepath, 'wb') as handle:
        pickle.dump(loc_to_country, handle)

    savepath = opt_dir+'unique_loc_{}_state_rule.pickle'.format(proc_num)
    with open(savepath, 'wb') as handle:
        pickle.dump(loc_to_state, handle)


    return_dict[proc_num] = [loc_to_country, loc_to_state, description_to_multi_loc]
        



def translate_multiprocessing(opt_dir, proc_num=10):
    processes = []

    manager = Manager()
    return_dict = manager.dict()

    start_time = time.time()

    city_path = '/pvol/geoparse/'

    print('multi processing starts')

    for w in range(proc_num):
        pickle_path = opt_dir+'tmp_{}.pickle'.format(w)
        
        p = Process(target=parse_location, args=(pickle_path, city_path, w, opt_dir, return_dict))

        p.daemon = True
        p.start()
        processes.append(p)

    for proc in processes:
        proc.join()

    end_time = time.time()

    print('\nProcessing time: {:.2f} hours {:.2f} mins'.format((end_time-start_time)/3600, ((end_time-start_time)%3600)/60))
    print('multi processing ends')

    return return_dict



if __name__ == "__main__":

    if not os.path.isdir(opt_dir):
        os.makedirs(opt_dir)
        
    with open(unique_locations_path, 'rb') as handle:
        unique_locations = set(pickle.load(handle))

    print('{} unique locations in total.'.format(len(unique_locations)))

    unique_locations_list = chunkIt(unique_locations, nproc)

    for i, sublist in enumerate(unique_locations_list):
        savepath = opt_dir+'tmp_{}.pickle'.format(i)
        with open(savepath, 'wb') as handle:
            pickle.dump(sublist, handle)

    return_dict = translate_multiprocessing(opt_dir=opt_dir, proc_num=nproc, world_parse=True)

    merged_dict_states_parsed = {}
    merged_dict_country_parsed = {}
    merged_dict_problem = {}

    for proc_num in return_dict.keys():

        proc_num_country_dict, proc_num_state_dict, description_to_multi_loc = return_dict[proc_num]

        for k, v in proc_num_country_dict.items():
            merged_dict_country_parsed[k] = v

        for k, v in proc_num_state_dict.items():
            merged_dict_states_parsed[k] = v

        for k, v in description_to_multi_loc.items():
            merged_dict_problem[k] = v

    dict_pickle_path = opt_dir+'unique_loc_parsed_country.pickle'
    with open(dict_pickle_path, 'wb') as handle:
        pickle.dump(merged_dict_country_parsed, handle, protocol=pickle.HIGHEST_PROTOCOL)

    dict_pickle_path = opt_dir+'unique_loc_parsed_states.pickle'
    with open(dict_pickle_path, 'wb') as handle:
        pickle.dump(merged_dict_states_parsed, handle, protocol=pickle.HIGHEST_PROTOCOL)

    dict_pickle_path = opt_dir+'problematic_loc_parsed.pickle'
    with open(dict_pickle_path, 'wb') as handle:
        pickle.dump(merged_dict_problem, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print('{} states parsed in total.'.format(len(merged_dict_states_parsed)))
    print('{} countries parsed in total.'.format(len(merged_dict_country_parsed)))
    print('{} problematic locations in total.'.format(len(merged_dict_problem)))
    
