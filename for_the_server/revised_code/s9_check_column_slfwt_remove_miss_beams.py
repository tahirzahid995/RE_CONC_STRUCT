import pandas as pd
import numpy as np
import json
import time
import pickle
import copy
from s7_refinement_functions import *
# from s2_Dataframe_to_dictionary import dict_list

# from s8_static_analysis import remove_repetitions_across_keys
# from s5_COMPARE_QUANTITY_OF_BEAMS_IN_YOUR_DICTI import minimum_nohouses


# from s8_static_analysis import grid_p_master

# daf = dict_list['B5']['DATAFRAME']
# print(list(daf.index[daf['IDs'].isin(['ID_8','ID_10'])]))




# # Specify the file path where you saved the dictionary
# file_path = "D:\OneDrive - Delft University of Technology\CORE\python files\Script_28_10_2023\grid_master.pkl"
# # Load the dictionary from the file using Pickle
# with open(file_path, 'rb') as file:
#     grid_p_master = pickle.load(file)

from pickle_commands import pickle_open
# Record the start time
# start_time = time.time()

# print('\n','---this code: PLACE NO COLUMNS AND SELFWEIGHT starts here---','\n')


# print(list(grid_p_master.keys())[:10])

# selecting (a) particular grid
# grid_p_master = {key: grid_p_master[key] for key in [(list(grid_p_master.keys())[100])]}
# print(f"grid is {list(grid_p_master.keys())}")

# with open("possible_grids.json", 'r') as file:
#     possible_grids = json.load(file)



disable_print = False  # Set this to True to disable all print functions

if disable_print:
    def print(*args, **kwargs):
        pass

# Your code here


##########################################   REMOVING NULL DICTIONARIES FROM REFINEMENT OUTPUT #############################
def removing_null_dictionaries(grid_p_master):
    # making a copy because the loop will be broken if the size of the dictionary being looped is changed
    grid_p_master_copy = copy.deepcopy(grid_p_master)
    # removing the null beam_types from the 'tra_qty_avail_ref' and 'tra_id_avail_ref' dictionaries
    for grid in grid_p_master_copy.keys():
            for l in grid_p_master_copy[grid]['tra_id_avail_ref'].keys():
                        for beam_type in grid_p_master_copy[grid]['tra_id_avail_ref'][l].keys():
                            if beam_type not in grid_p_master_copy[grid]['tra_qty_req'][l]:
                                del grid_p_master[grid]['tra_id_avail_ref'][l][beam_type]
                                del grid_p_master[grid]['tra_qty_avail_ref'][l][beam_type]
    return grid_p_master


#################################################    NUMBER OF COLUMNS  #################################################
def find_number_of_columns(grid_p_master):
    for grid in grid_p_master:
        grid_p_master[grid]['column_qty'] = (len(grid_p_master[grid]['beams']['x'])+1) * (len(grid_p_master[grid]['beams']['y'])+1)
    return grid_p_master

#################################################    SOLVER FOR SELFWEIGHT  ####################################################


def solver_for_selfweight(dict_list,grid_p_master, h):
    # Generating a dictionary of IDs of the Dataframe sorted according to the weight
    dict_position =  {}
    dict_position['by_weight']={}
    for beam_type in dict_list.keys():
        if beam_type in dict_list and 'DATAFRAME' in dict_list[beam_type]:
            dframe = dict_list[beam_type]['DATAFRAME']
            dict_position['by_weight'][beam_type]= {}
            dict_position['by_weight'][beam_type] = sort_dataframe_by_column(dframe,'weight')



    # # number of houses (variable connected to rest of the script)
    # h = minimum_nohouses
    # number of houses (variable independant to rest of the script)
    



    for grid in grid_p_master.keys():
        grid_p_master[grid]['number_of_houses'] = 0
        grid_p_master[grid]['weight'] = {}
        grid_p_master[grid]['weight']['wt_per_house'] = 0
        grid_p_master[grid]['weight']['total_wt'] = 0
        grid_p_master[grid]['tra_id_avail_ref_wtsorted'] = {}
        grid_p_master[grid]['tra_id_used_ref_wtsorted'] = {}
        grid_p_master[grid]['tra_qty_used_ref_wtsorted'] = {}
        grid_p_master[grid]['tra_qty_req_h'] = {}

        grid_p_master[grid]['missing_beams'] ={}
        missing_beams_total = 0
        grid_p_master[grid]['missing_beams']['yes/no'] = 'no'
        grid_p_master[grid]['missing_beams']['qty_each'] = {}
        h_qty_potential_list = []

        for l in grid_p_master[grid]['tra_id_avail_ref'].keys():

            # making dictionary
            grid_p_master[grid]['tra_id_avail_ref_wtsorted'][l] = {}
            used_id_sorted = grid_p_master[grid]['tra_id_used_ref_wtsorted'][l] = {}
            grid_p_master[grid]['tra_qty_req_h'][l] = {}
            grid_p_master[grid]['missing_beams']['qty_each'][l] = {}
            grid_p_master[grid]['tra_qty_used_ref_wtsorted'][l] = {}
            
            # assigning variable for cleaner script
            avail_id_sorted = grid_p_master[grid]['tra_id_avail_ref_wtsorted'][l]
            used_id_sorted = grid_p_master[grid]['tra_id_used_ref_wtsorted'][l]
            req_qty_h = grid_p_master[grid]['tra_qty_req_h'][l]
            
            

            for beam_type in grid_p_master[grid]['tra_id_avail_ref'][l].keys():

                # making dictionary
                avail_id_sorted[beam_type] = {}
                used_id_sorted[beam_type] = {}
                req_qty_h[beam_type]={}
                grid_p_master[grid]['missing_beams']['qty_each'][l][beam_type] = {}
                grid_p_master[grid]['tra_qty_used_ref_wtsorted'][l][beam_type] = {}
                df_1 = dict_list[beam_type]['DATAFRAME']
                

                for area, ids in grid_p_master[grid]['tra_id_avail_ref'][l][beam_type].items():
                
                    # making dictionary
                    avail_id_sorted[beam_type][area]={}
                    used_id_sorted[beam_type][area]={}
                    req_qty_h[beam_type][area]={}
                    grid_p_master[grid]['missing_beams']['qty_each'][l][beam_type][area] = {}
                    grid_p_master[grid]['tra_qty_used_ref_wtsorted'][l][beam_type][area] = {}

                    # required number of beams for h houses
                    req_qty_for_1_house = grid_p_master[grid]['tra_qty_req'][l][beam_type][area]
                    req_qty_for_h_houses = req_qty_for_1_house*h
                    req_qty_h[beam_type][area] = req_qty_for_h_houses
                    
                    # sorting the available beams for that area according to self-weight
                    sorted_id = sort_nested_dic_acc_to_dataframe_column_2(ids, dict_position['by_weight'][beam_type] )

                    # selecting the lightest beams out of the sorted ones for h number of house
                    used_id = sorted_id[: req_qty_for_h_houses]
                    # else: 
                    #     for i in range(1,h,1):
                    #         if req_qty_for_h_houses - req_qty_for_1_house*i < len(sorted_id):
                    #             print(f"for {h-i} houses, req beams are {req_qty_for_h_houses - req_qty_for_h_houses*i}. id is {sorted_id[:req_qty_for_h_houses - req_qty_for_h_houses*i]}")
                    #             break

                        

                    # calculating the self-weight of beam for h houses
                    sorted_indices = list(df_1.index[df_1['IDs'].isin(used_id)])
                    wt = round(sum(list(df_1.loc[sorted_indices, 'weight'])))

                    # calculating the average self-weight of beam for 1 house
                    avg_wt = round(wt/ h) 

                    grid_p_master[grid]['weight']['wt_per_house'] += avg_wt
                    grid_p_master[grid]['weight']['total_wt'] += wt


                    avail_id_sorted[beam_type][area] = sorted_id
                    used_id_sorted[beam_type][area] = used_id
                    grid_p_master[grid]['tra_qty_used_ref_wtsorted'][l][beam_type][area] = len(used_id)


                    # number of houses possible
                    h_qty_potential = math.floor(len(sorted_id) / req_qty_for_1_house)

                    h_qty_potential_list.append(h_qty_potential)
                    

                    # if req quantity is satisfied for required houses
                    if req_qty_for_h_houses <= len(sorted_id):
                        pass
                    else:
                        # number of missing beams
                        mb = req_qty_for_h_houses - len(sorted_id)
                        missing_beams_total += mb
                        grid_p_master[grid]['missing_beams']['qty_each'][l][beam_type][area] = mb
                        grid_p_master[grid]['missing_beams']['yes/no'] = 'yes'
                        grid_p_master[grid]['missing_beams']['qty_total'] = missing_beams_total

        grid_p_master[grid]['number_of_houses'] = sorted(h_qty_potential_list)[0]

    return grid_p_master

### THIS DOES NOT TAKE INTO ACCOUNT IF MISSING BEAMS ARE IN X AND NOT Y OR VICE-VERSA!


################################################   FILTERING FOR REQUIRED NUMBER OF HOUSES  ####################################

def filtering_for_required_no_houses(grid_p_master):
    # filtering the grids with required number of houses
    grid_master_2 = {}
    usable_grids = 0
    max_number_of_houses_list = []
    for grid in grid_p_master.keys():
            condition = grid_p_master[grid]['missing_beams']['yes/no']
            if condition == 'no':
                grid_new = grid_p_master[grid]
                grid_master_2[grid] = grid_new
                usable_grids += 1

    if usable_grids == 0:
        for grid in grid_p_master.keys():
            max_number_of_houses_list.append(grid_p_master[grid]['number_of_houses'])
        max_number_of_houses = sorted(max_number_of_houses_list)[-1]
                 

        print('---')
        print('Zero usable grids found')
        print('---')
        print('New stock is needed for required number of houses you have input')
        print('---')
        print(f"The max number of houses for this input are {max_number_of_houses}")
        print('---')
    else:
        print('---')
        print(f"{usable_grids} usable grids found")
        print('---')
    return grid_master_2    


################################################   TEST SAMPLE DATA  ########################################################

'''#x has available id
avail_id_sample = {'B3': {2.25: [24, 59, 74, 246, 280, 339, 376, 446, 502, 520, 555, 615, 656, 706, 893, 907, 954, 1044, 1058], 
        4.5: [45, 71, 123, 277, 316, 357, 382, 486, 507, 543, 571, 631, 665, 728, 898, 947, 1030, 1049]}, 
        'B4': {}, 'B5': {}}
#x has available qty
avail_qty_sample = {'B3': {2.25: 19, 4.5: 18}, 'B4': {}, 'B5': {}}
#x has required 
req_qty_sample = {'B3': {2.25: 12, 4.5: 6}}
'''

################################################   TESTING SELFWEIGHT  ########################################################

'''
print('---PRINTING CODE: PLACE NO COLUMNS AND SELFWEIGHT STARTS HERE---')

grid_to_test=(list(grid_p_master.keys())[0])
b_type = 'B3'
print(grid_to_test)

print('---HERE---')
print(f"beams are {grid_p_master[grid_to_test]['beams']}")
print('---HERE---')
print(f"refined avail_qty in x are {grid_p_master[grid_to_test]['tra_qty_avail_ref']['x'][b_type]}")
print('---HERE---')
print(f"unrefined avail_qty in x are {grid_p_master[grid_to_test]['tra_qty_avail']['x'][b_type]}")
# print('---HERE---')
# print(f"missing_beams is {grid_p_master[grid_to_test]['missing_beams']}")
# print('---HERE---')
# print(f"weight is {grid_p_master[grid_to_test]['weight']}")
# print('---HERE---')
# print(f"Column quantity is {grid_p_master[grid_to_test]['column_qty']}")
print('---HERE---')
print(f"req_qty for 1 house are {grid_p_master[grid_to_test]['tra_qty_req']['x'][b_type]}")
# print('---HERE---')
# print(f"used_id_sorted are {grid_p_master[grid_to_test]['tra_id_used_ref_wtsorted']}")
print('---HERE---')
print(f"required_qty for {h} houses are {grid_p_master[grid_to_test]['tra_qty_req_h']['x'][b_type]}")
# print('---HERE---')
# print(f"used_qty_sorted are {grid_p_master[grid_to_test]['tra_qty_used_ref_wtsorted']}")
# print('---HERE---')
# print(f"tributary loading area are")
# print(grid_p_master[grid_to_test]['tr_area']['x'])
print('---HERE---')
print(f"keys are {list(grid_p_master[grid_to_test].keys())}")
print('---HERE---')
print(f"master grid with missing beam grids has {len(list(grid_p_master.keys()))} keys")
print('---HERE---')
print(f"master grid without missing beam grids has {len(list(grid_master_2.keys()))} keys")
print(dict_list.keys())

# # testing the sorting function for the problematic grid 
# ids = [24,59,74,246,280,339,376,446,502,520,555,615,656,706,893,907,954,1044,1058]
# df = dict_list['B3']['DATAFRAME']
# sorted_id = sort_nested_dic_acc_to_dataframe_column(ids,df)
# print(sorted_id)'''


'''tr_area_test = grid_p_master[grid_to_test]['tr_area']['x']
#SAVE DATAFRAME TO CSV
tr_area_test.to_csv('D:/OneDrive - Delft University of Technology/CORE/python files/Script 24_10_2023/tr_area_test.csv',index=None)

# Record the end time
end_time = time.time()
# Calculate the execution time
execution_time = end_time - start_time
print(f"Execution time using time module: {round(execution_time*1000,3)} milliseconds")


# SAVING GRID_P_MASTER TO PICKLE AS GRID_MASTER_1
# Specify the file path where you want to save the dictionary
file_path = "D:\OneDrive - Delft University of Technology\CORE\python files\Script_28_10_2023\grid_master_1.pkl"
# Save the dictionary to a file using Pickle
with open(file_path, 'wb') as file:
    pickle.dump(grid_p_master, file)

# SAVING GRID_MASTER_2 TO PICKLE AS GRID_MASTER_2
# Specify the file path where you want to save the dictionary
file_path = "D:\OneDrive - Delft University of Technology\CORE\python files\Script_28_10_2023\grid_master_2.pkl"
# Save the dictionary to a file using Pickle
with open(file_path, 'wb') as file:
    pickle.dump(grid_master_2, file)
'''