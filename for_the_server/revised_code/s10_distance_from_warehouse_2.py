import pandas as pd
import numpy as np
import json
import time
import pickle
import copy
import matplotlib.pyplot as plt
import folium
import math
import itertools
import pprint 
# from s2_Dataframe_to_dictionary import dict_list
# from s0_preDataframe import *
# from s9_Place_no_columns_and_selfweight_version1 import h
from s7_refinement_functions import *

# pp = pprint.PrettyPrinter()

# h = 10

def distance_from_warehouse(grid_p_master_2, locations_warehouses, combinations_wh, dict_list, h, weight_per_truck):
    
    ######################################################## INPUTS #############################################

    # distance_per_warehouse = locations_warehouses[name]['distance']

    # # testing all grids
    # grid_master_to_test = grid_p_master_2
    # print(len((list(grid_master_to_test.keys()))))

    # testing selective grids
    grid_master_to_test = grid_p_master_2
    # grid_master_to_test = filter_dictionary(grid_master_to_test, 10)
    # print(len((list(grid_master_to_test.keys()))))

    ######################################################## SOLVER #############################################



    # Making dictionaries for weight
    for grid in grid_master_to_test.keys():
        grid_master_to_test[grid]['weight'] = {}
        grid_master_to_test[grid]['weight']['wt_per_wh']= {}
        grid_master_to_test[grid]['weight']['wt_total']= {}
        for wh_comb in combinations_wh:
            grid_master_to_test[grid]['weight']['wt_per_wh'][str(wh_comb)] = {}
            grid_master_to_test[grid]['weight']['wt_total'][str(wh_comb)] = 0
            for wh in wh_comb:
                grid_master_to_test[grid]['weight']['wt_per_wh'][str(wh_comb)][wh]=0


    # SOLVER

    for grid in grid_master_to_test.keys():

        # remaking dictionaries which have been formed for average selfweight of all warehouses
        grid_master_to_test[grid]['tra_id_avail_ref_wtsorted'] = {}
        grid_master_to_test[grid]['tra_id_used_ref_wtsorted'] = {}
        grid_master_to_test[grid]['tra_qty_used_ref_wtsorted'] = {}
        
        grid_master_to_test[grid]['missing_beams'] ={}
        grid_master_to_test[grid]['missing_beams']['yes/no'] = {}
        grid_master_to_test[grid]['missing_beams']['qty_each'] = {}
        grid_master_to_test[grid]['missing_beams']['qty_total'] = {}
        
        # making new dictionaries 
        grid_master_to_test[grid]['distance'] = {}
        grid_master_to_test[grid]['distance']['dist_total'] = {}
        grid_master_to_test[grid]['distance']['dist_per_wh'] = {}
        grid_master_to_test[grid]['distance']['trips_per_wh'] = {}

        
        for wh_comb in combinations_wh:
            grid_master_to_test[grid]['weight']['wt_per_wh'][str(wh_comb)][wh] = 0
            missing_beams_total_by_dis = 0

            grid_master_to_test[grid]['distance']['dist_total'][str(wh_comb)]= 0
            grid_master_to_test[grid]['distance']['dist_per_wh'][str(wh_comb)]= {}
            grid_master_to_test[grid]['distance']['trips_per_wh'][str(wh_comb)]= {}

            grid_master_to_test[grid]['missing_beams']['yes/no'][str(wh_comb)] = 'no'
            grid_master_to_test[grid]['missing_beams']['qty_each'][str(wh_comb)] = {}
            
            # making dictionary sort by distance
            grid_master_to_test[grid]['tra_id_avail_ref_wtsorted'][str(wh_comb)] = {}
            grid_master_to_test[grid]['tra_id_used_ref_wtsorted'][str(wh_comb)] = {}
            grid_master_to_test[grid]['tra_qty_used_ref_wtsorted'][str(wh_comb)] = {}
            grid_master_to_test[grid]['missing_beams']['qty_each'][str(wh_comb)] = {}


            for l in grid_master_to_test[grid]['tra_id_avail_ref'].keys():

                # making dictionary
                grid_master_to_test[grid]['tra_qty_req_h'][l] = {}
            

                grid_master_to_test[grid]['tra_id_avail_ref_wtsorted'][str(wh_comb)][l] = {}
                grid_master_to_test[grid]['tra_id_used_ref_wtsorted'][str(wh_comb)][l] = {}
                grid_master_to_test[grid]['tra_qty_used_ref_wtsorted'][str(wh_comb)][l] = {}
                grid_master_to_test[grid]['missing_beams']['qty_each'][str(wh_comb)][l] = {}

                
                # assigning variable for cleaner script 
                req_qty_h = grid_master_to_test[grid]['tra_qty_req_h'][l]

                # assigning variable for cleaner script (sort by distance)
                avail_id_sorted_by_dis = grid_master_to_test[grid]['tra_id_avail_ref_wtsorted'][str(wh_comb)][l]
                used_id_sorted_by_dis = grid_master_to_test[grid]['tra_id_used_ref_wtsorted'][str(wh_comb)][l]




                for beam_type in grid_master_to_test[grid]['tra_id_avail_ref'][l].keys():

                    # making dictionary
                    req_qty_h[beam_type]={}

                    # making dictionary sort by weight
                    avail_id_sorted_by_dis[beam_type] = {}
                    used_id_sorted_by_dis[beam_type] = {}

                    # making dictionary sort by distance
                    grid_master_to_test[grid]['missing_beams']['qty_each'][str(wh_comb)][l][beam_type] = {}
                    grid_master_to_test[grid]['tra_qty_used_ref_wtsorted'][str(wh_comb)][l][beam_type] = {}
                    
                    df_1 = dict_list[beam_type]['DATAFRAME']


                    for area, ids in grid_master_to_test[grid]['tra_id_avail_ref'][l][beam_type].items():
                    
                        # making dictionary sort by distance
                        avail_id_sorted_by_dis[beam_type][area]={}
                        used_id_sorted_by_dis[beam_type][area]={}

                        # making dictionary sort by distance
                        grid_master_to_test[grid]['missing_beams']['qty_each'][str(wh_comb)][l][beam_type][area] = {}
                        grid_master_to_test[grid]['tra_qty_used_ref_wtsorted'][str(wh_comb)][l][beam_type][area] = {}

                        req_qty_h[beam_type][area]={}

                        # required number of beams for h houses
                        req_qty_for_1_house = grid_master_to_test[grid]['tra_qty_req'][l][beam_type][area]
                        req_qty_for_h_houses = req_qty_for_1_house *h
                        req_qty_h[beam_type][area] = req_qty_for_h_houses
                        

                        ###################################### SORT BY DISTANCE ###############################################
                    


                        # sort a dictionary of beams from wh_comb : the selected warehouses
                        dict_position_by_dis = sort_dataframe_by_columnA_whilst_refining_by_columnB(df_1, 'weight', 'Warehouse', wh_comb )

                        # sorting the available beams for that area according to self-weight
                        sorted_id_by_dis = sort_nested_dic_acc_to_dataframe_column_2(ids, dict_position_by_dis)

                        # selecting the lightest beams out of the sorted ones for h number of house
                        used_id_by_dis = sorted_id_by_dis[: req_qty_for_h_houses]
                        
                        # indices_beams = list(df.index[df['IDs'].isin(['ID_37791','ID_13341'])])
                        # weights = list(df.loc[indices_beams]['weight'])
                        # weights_sorted = sorted(weights)

                    
                        for wh in wh_comb:

                            # position_dict of warehouse (wh)
                            dict_position_by_dis_wh = sort_dataframe_by_columnA_whilst_refining_by_columnB(df_1, 'weight', 'Warehouse', [wh] )
                            # filtering ids that are in warehouse (wh)
                            sort_id_by_dis_wh = [i for i in used_id_by_dis if i in dict_position_by_dis_wh]

                            # calculating the self-weight of beam for h houses for each warehouse combination 
                            sorted_indices_by_dis = list(df_1.index[df_1['IDs'].isin(sort_id_by_dis_wh)])
                            wt_by_dis_per_warehouse = round(sum(list(df_1.loc[sorted_indices_by_dis, 'weight'])))

                            # self-weight for each warehouse (wh) in each combination
                            grid_master_to_test[grid]['weight']['wt_per_wh'][str(wh_comb)][wh] += wt_by_dis_per_warehouse
                            

                            avail_id_sorted_by_dis[beam_type][area] = sorted_id_by_dis
                            used_id_sorted_by_dis[beam_type][area] = used_id_by_dis
                            grid_master_to_test[grid]['tra_qty_used_ref_wtsorted'][str(wh_comb)][l][beam_type][area] = len(used_id_by_dis)

                        # if req quantity is satisfied
                        if req_qty_for_h_houses <= len(sorted_id_by_dis):
                            pass
                        else:
                            # number of missing beams
                            mb_by_dis = req_qty_for_h_houses - len(sorted_id_by_dis)
                            missing_beams_total_by_dis += mb_by_dis
                            grid_master_to_test[grid]['missing_beams']['qty_each'][str(wh_comb)][l][beam_type][area] = mb_by_dis
                            grid_master_to_test[grid]['missing_beams']['yes/no'][str(wh_comb)] = 'yes'
                            grid_master_to_test[grid]['missing_beams']['qty_total'][str(wh_comb)] = missing_beams_total_by_dis



    # Finding total distance, weight, and number of trips for each warehouse combination

    for grid in grid_master_to_test.keys():
        for wh_comb in combinations_wh:    
            for wh in wh_comb:

                # weight per warehouse (variable to better readability)s
                weight_per_warehouse = grid_master_to_test[grid]['weight']['wt_per_wh'][str(wh_comb)][wh]
                

                # distance per warehouse (remains a constant for all grids)
                distance_per_warehouse = locations_warehouses[wh]['distance']

                number_of_trips_per_warehouse = math.ceil(weight_per_warehouse / weight_per_truck)
                total_distance_per_warehouse = round(number_of_trips_per_warehouse * distance_per_warehouse)

                # number of trips per warehouse
                grid_master_to_test[grid]['distance']['trips_per_wh'][str(wh_comb)][wh] = 0
                grid_master_to_test[grid]['distance']['trips_per_wh'][str(wh_comb)][wh] = number_of_trips_per_warehouse            

                # total distance per warehouse
                grid_master_to_test[grid]['distance']['dist_per_wh'][str(wh_comb)][wh] = 0
                grid_master_to_test[grid]['distance']['dist_per_wh'][str(wh_comb)][wh] = total_distance_per_warehouse

                # total distance per warehouse combination
                grid_master_to_test[grid]['distance']['dist_total'][str(wh_comb)]+= total_distance_per_warehouse 

                # total weigth per warehouse combination
                grid_master_to_test[grid]['weight']['wt_total'][str(wh_comb)] += weight_per_warehouse

    return grid_master_to_test

            
def grids_with_keys_as_objectives(grid_master_to_test):
    
    # For each grid, finding warehouse combination for least weight and least distance
    dict_objective_wh_comb={}
    # dict_optimized_wh_comb = {}

    for grid in grid_master_to_test.keys():
        # filtering out the combinations where there are missing beams
        comb_with_no_missing_beams = [key for key,value in grid_master_to_test[grid]['missing_beams']['yes/no'].items() if value == 'no']
        
        objective_dict = {}
        dict_objective_wh_comb[grid]={}
        # dict_optimized_wh_comb[grid]={}

        for wh_comb in comb_with_no_missing_beams:
            wh_comb = str(wh_comb)
            
            dict_objective_wh_comb[grid][wh_comb]={}
            objective_dict[wh_comb] = {}
            
            dict_objective_wh_comb[grid][wh_comb]['distance'] = grid_master_to_test[grid]['distance']['dist_total'][str(wh_comb)]
            dict_objective_wh_comb[grid][wh_comb]['weight'] = grid_master_to_test[grid]['weight']['wt_total'][str(wh_comb)]
            objective_dict[wh_comb]['distance'] = grid_master_to_test[grid]['distance']['dist_total'][str(wh_comb)]
            objective_dict[wh_comb]['weight'] = grid_master_to_test[grid]['weight']['wt_total'][str(wh_comb)]

        # optimized_wh_comb_weight = min(objective_dict, key=lambda k: (objective_dict[k]['weight']))
        # optimized_wh_comb_distance = min(objective_dict, key=lambda k: (objective_dict[k]['distance']))

        # dict_optimized_wh_comb[grid]['distance'] = optimized_wh_comb_distance
        # dict_optimized_wh_comb[grid]['weight'] = optimized_wh_comb_weight

    return dict_objective_wh_comb
 

################################################   TESTING  ########################################################


'''print('---PRINTING CODE: DISTANCE FROM WAREHOUSE starts here---')


# # pp.pprint(objective_dict)
# print(f"{grid} optimized distance = {optimized_wh_comb_distance}")
# print(f"{grid} optimized weight = {optimized_wh_comb_weight}")
# print(dict_optimized_wh_comb)



# testing dict_list['DATAFRAME]
# val_tot = 0
# for beam_type in dict_list.keys():
#     df_spliced = dict_list[beam_type]['DATAFRAME']
#     val = len(df_spliced.index)
#     print(f"df_spliced {beam_type} has {val} values")

#     for wh in warehouses:
#         id = df_spliced[df_spliced['Warehouse'].isin([wh])]
#         print(f"{wh} has {len(id)}")
                                
#     val_tot += val
# print(f"df_spliced has total {val_tot} values ")
# print('---')
# print(f"df has {len(list(df.index))} values")



# df_test = dict_list['B4']['DATAFRAME']
# wh_test = combinations_wh[5]
# test = sort_dataframe_by_columnA_whilst_refining_by_columnB(df_test, 'weight', 'Warehouse', wh_test)
# print(f"filtered values are {len(test)}")
# print(f"total values are {len(sort_dataframe_by_column(df_test, 'weight'))}")





# print(grid_master_to_test.keys())
# for grid in grid_master_to_test.keys():
#     pp.pprint({key: value for key,value in grid_master_to_test[grid]['missing_beams']['yes/no'].items() if value == 'no'})
    # for wh_comb in combinations_wh:
    # print(grid_master_to_test[grid]['distance']['dist_per_wh'])
    # print(grid_master_to_test[grid]['weight']['wt_per_wh'])
    # pp.pprint(grid_master_to_test[grid]['distance']['dist_total'])
    # print('---')
    
    
        

# grid_to_test=(list(grid_master_to_test.keys())[0])
# b_type = 'B3'
# print(grid_to_test)

# print('---HERE---')
# print(f"beams are {grid_master_to_test[grid_to_test]['beams']}")
# print('---HERE---')
# # print(f"avail_id in x are {grid_master_to_test[grid_to_test]['tra_id_avail_ref']['x']}")
# # print('---HERE---')
# # print(f"avail_id in y are {grid_master_to_test[grid_to_test]['tra_id_avail_ref']['y']}")
# # print('---HERE---')
# print(f"missing_beams is {grid_master_to_test[grid_to_test]['missing_beams']}")
# print('---HERE---')
# print(f"weight is {grid_master_to_test[grid_to_test]['weight']}")
# print('---HERE---')
# print(f"Column quantity is {grid_master_to_test[grid_to_test]['column_qty']}")
# print('---HERE---')
# # print(f"avail_id_sorted are {grid_master_to_test[grid_to_test]['tra_id_avail_ref_wtsorted']}")
# # print('---HERE---')
# print(f"used_id_sorted are {grid_master_to_test[grid_to_test]['tra_id_used_ref_wtsorted']}")
# print('---HERE---')
# print(f"required_qty_sorted are {grid_master_to_test[grid_to_test]['tra_qty_req_h']}")
# print('---HERE---')
# print(f"used_qty_sorted are {grid_master_to_test[grid_to_test]['tra_qty_used_ref_wtsorted']}")
# print('---HERE---')
# print(f"tributary loading area are")
# print(grid_master_to_test[grid_to_test]['tr_area']['x'])
# # print('---HERE---')
# # print(f"keys are {list(grid_master_to_test[grid_to_test].keys())}")
# print('---HERE---')
# print(f"master grid has {len(list(grid_master_to_test.keys()))} keys")
# print('---HERE---')
# print(f"master grid has {len(list(grid_master_to_test.keys()))} keys")'''




######################################################## END ########################################################

'''

# Record the end time
end_time = time.time()
# Calculate the execution time
execution_time = end_time - start_time
print(f"Execution time using time module: {round(execution_time*1000,3)} milliseconds")





# SAVING GRID_MASTER_TO_TEST TO PICKLE AS GRID_MASTER_3
# Specify the file path where you want to save the dictionary
file_path = "D:\OneDrive - Delft University of Technology\CORE\python files\Script_28_10_2023\grid_master_3.pkl"
# Save the dictionary to a file using Pickle
with open(file_path, 'wb') as file:
    pickle.dump(grid_master_to_test, file)



# SAVING dict_optimized_wh_comb TO PICKLE AS dict_optimized_wh_comb
# Specify the file path where you want to save the dictionary
file_path = "D:\OneDrive - Delft University of Technology\CORE\python files\Script_28_10_2023\dict_optimized_wh_comb.pkl"
# Save the dictionary to a file using Pickle
with open(file_path, 'wb') as file:
    pickle.dump(dict_optimized_wh_comb, file)



# SAVING dict_objective_wh_comb TO PICKLE AS dict_objective_wh_comb
# Specify the file path where you want to save the dictionary
file_path = "D:\OneDrive - Delft University of Technology\CORE\python files\Script_28_10_2023\dict_objective_wh_comb.pkl"
# Save the dictionary to a file using Pickle
with open(file_path, 'wb') as file:
    pickle.dump(dict_objective_wh_comb, file)'''