import pandas as pd
import numpy as np
import time
import pickle
import copy
import matplotlib.pyplot as plt
import folium
import math
import itertools
import pprint 
from s7_refinement_functions import *
# from s2_Dataframe_to_dictionary import dict_list
import plotly.graph_objects as go
import pprint
import time
import csv


pp = pprint.PrettyPrinter()



# print('\n','---this code:  S_12 BEAM DISTRIBUTION FOR BEST GRID starts here---','\n')


'''
grid = grid_p_master_3['grid_6803']
print(grid['tra_id_used_ref_wtsorted'].keys())
wh = ['Warehouse_1','Warehouse_2','Warehouse_4','Warehouse_5', 'Warehouse_6', 'Warehouse_7', 'Warehouse_8']


print(grid['tra_qty_req']['x']['B4'])
print(grid['tra_qty_req_h']['x']['B4'])
'''
def reorder_alternate(x):
    '''
    # DESCRIPTION: reorders a list. Works if len(x) is odd or even 

    # INPUT: x is a list
    for eg. x = [1,2,3,4,5,6,7,8,9,10]

    # OUTPUT: 
    x = [1,10,2,9,3,8,4,7,5,6]
    '''

    # Initialize an empty list for y
    y = []

    # Loop through the elements in x and reorder them in y
    for i in range(len(x)//2):
        y.append(x[i])
        y.append(x[-(i + 1)])
    # If x has an odd number of elements, add the middle element to y
    if len(x) % 2 != 0:
        y.append(x[len(x)//2])

    return y

# h, warehouses

# DEFINE HOUSES
# h = 10

def beam_distribution_for_best_grid(grid, h, wh, house_index,df):
    '''
    # DESCRIPTION: Makes a dictionary for the best grid. 

    # INPUT: 
    1) grid is a dictionary of a single grid.
    it is one grid obtained from the master grid which contains only number of grid. 
    e.g grid = grid_p_master_3['grid_6803'] 

    2) h is the number of houses

    3) wh is the list of warehouses.
    eg. wh = ['Warehouse_1','Warehouse_2','Warehouse_4','Warehouse_5', 'Warehouse_6', 'Warehouse_7', 'Warehouse_8']

    4) house_index is a list of all ids of houses
    eg. house_index = [house_1, house_2, house_3, house_4, house_5]
    '''

    grid_houses = {}

    # properties that are the same of individual houses
    grid_houses['distance'] = grid['distance']['dist_total'][str(wh)]
    grid_houses['tr_area'] = {}
    grid_houses['beams'] = {}
    grid_houses['tr_area'] =  grid['tr_area']
    grid_houses['beams'] =  grid['beams']        

    # properties that are different for individual houses
    grid_houses['tra_id_used_ref_wtsorted'] = {}
    grid_houses['weight_per_house'] = {}
    grid_houses['ids_per_warehouse'] = {}
    grid_houses['ids_all'] = {}
    weight_total = 0



    ## Making dictionaries
    for hs in house_index:

        # new dictionaries
        grid_houses['tra_id_used_ref_wtsorted'][hs] = {}
        grid_houses['weight_per_house'][hs] = 0
        grid_houses['ids_per_warehouse'][hs] = {}
        grid_houses['ids_all'][hs] = []
        weight_total = 0

        for warehouse in wh:
            grid_houses['ids_per_warehouse'][hs][warehouse] = []



    ## Assigning beam ids to each house and calculating the total weight of  each house

    for hs in house_index:

        for l in  grid['tra_id_used_ref_wtsorted'][str(wh)]:
            grid_houses['tra_id_used_ref_wtsorted'][hs] [l] = {}
            
            for beam_type in grid['tra_id_used_ref_wtsorted'][str(wh)][l]:
                grid_houses['tra_id_used_ref_wtsorted'][hs][l][beam_type]={}

                for area in grid['tra_id_used_ref_wtsorted'][str(wh)][l][beam_type]:
                    grid_houses['tra_id_used_ref_wtsorted'][hs] [l][beam_type][area]={}
                    
                    req_beams_qty_per_house = grid['tra_qty_req'][l][beam_type][area]
                    id_beams = grid['tra_id_used_ref_wtsorted'][str(wh)][l][beam_type][area]

                    # re orders the beams so 1 lightest, 1 heaviest is chosen so all houses have a moderate weight
                    id_beams_re = reorder_alternate(id_beams)

                    id_beams_per_house = id_beams_re[:req_beams_qty_per_house]

                    # checking weights
                    indices_beams = list(df.index[df['IDs'].isin(id_beams_per_house)])
                    weight = round(sum(list(df.loc[indices_beams]['weight'])))
                    weight_total += weight
                    
                    grid_houses['tra_id_used_ref_wtsorted'][hs][l][beam_type][area] = id_beams_per_house
                    grid_houses['weight_per_house'][hs]  = weight_total

                    grid_houses['ids_all'][hs].append(id_beams_per_house)



    ## Assgining beam ids for each warehouse for tracking what ids are needed from which wareshouse

    for hs in house_index:

        all_beams = grid_houses['ids_all'][hs]
        flat_list = []
        for sublist in all_beams:
            for i in sublist:
                flat_list.append(i)
    
        
        for warehouse in wh:
            
            all_warehouse_ids = (list(df[df['Warehouse'].isin([warehouse])]['IDs']))     
            grid_houses['ids_per_warehouse'][hs][warehouse] = [i for i in flat_list if i in all_warehouse_ids]
            




    ## Assigning ids (and making dataframes for their depths, and widths) to each beam position in each house

    ids_copy = copy.deepcopy(grid_houses['tra_id_used_ref_wtsorted'])
    grid_houses['ids_dataframe'] = {}
    grid_houses['widths_dataframe'] = {}
    grid_houses['depths_dataframe'] = {}
    grid_houses['lengths_dataframe'] = {}

    for hs in house_index:

        grid_houses['ids_dataframe'][hs] = {}
        grid_houses['widths_dataframe'][hs]= {}
        grid_houses['depths_dataframe'][hs]= {}
        grid_houses['lengths_dataframe'][hs]= {}

        for l in grid_houses['tr_area']:
            

            grid_houses['ids_dataframe'][hs][l] = pd.DataFrame()
            grid_houses['widths_dataframe'][hs][l] = pd.DataFrame()
            grid_houses['depths_dataframe'][hs][l] = pd.DataFrame()
            grid_houses['lengths_dataframe'][hs][l] = pd.DataFrame()

            for beam_type_column in grid_houses['tr_area'][l].columns:
                beam_type = beam_type_column[-2:]

                # properties for each beam in that position. for instance if x =[A-B3,B-B4,C-B5,D-B3], id_each will be ids for all the A-B3s
                id_each = []
                width_each = []
                depth_each = []
                length_each = []

                for i, area in enumerate (grid_houses['tr_area'][l][beam_type_column]):              
                    
                    id = str(ids_copy[hs][l][beam_type][area][0]) 
                    del ids_copy[hs][l][beam_type][area][0]

                    weight = float(df.loc[df['IDs'] == id,'weight'].values[0])
                    depth = float(df.loc[df['IDs'] == id,'depth'].values[0])
                    length = float(df.loc[df['IDs'] == id,'lengths'].values[0])
                    width = float(df.loc[df['IDs'] == id,'width'].values[0])

                    id_each.append(id)
                    width_each.append(width)
                    depth_each.append(depth)
                    length_each.append(length)

                grid_houses['ids_dataframe'][hs][l][beam_type_column] = id_each
                grid_houses['widths_dataframe'][hs][l][beam_type_column] = width_each
                grid_houses['depths_dataframe'][hs][l][beam_type_column] = depth_each
                grid_houses['lengths_dataframe'][hs][l][beam_type_column] = length_each
            

    # Convert weight per warehouse dictionary into dataframe
    grid_houses['weight_per_house'] = pd.DataFrame(list(grid_houses['weight_per_house'].items()), columns=['House', 'Weight/KN'])
    grid_houses['weight_per_house']['Weight/KN'] = grid_houses['weight_per_house']['Weight/KN'] /1000

    return grid_houses


# ################################################   TESTING  ########################################################

'''
print('---PRINTING CODE: S_12 BEAM DISTRIBUTION FOR BEST GRID STARTS HERE---')

print(grid_houses.keys())
print(grid_houses['ids_dataframe']['house_1']['x'])
print('---')
print(grid_houses['weight_per_house'])
print('---')
print(grid_houses['depths_dataframe']['house_1']['x'])
pp.pprint(grid_houses['ids_per_warehouse']['house_1'])
print(grid_houses['weight_per_house']['house_1'])
print(grid_houses['distance'])
print(grid_houses['tr_area']['x'])
print(grid_houses['beams'])

dfb4 = dict_list['B4']['DATAFRAME']
print(len(dfb4))
'''





# EXPORTING DICTIONARIES TO CSV
def print_csv_dict(dict_1, key_name, subkey_name, file_path_name):
    '''
    # DESCRIPTION: prints a nested dictionary to a csv

    # INPUTS:
    dict_1 is a dictionary
    key_name and subkey_name are strings which are going to be the column header

    # OUTPUTS: a csv with two columns in the order represented
    '''
    # Specify the output CSV file path
    output_file = file_path_name

    # Write the dictionary to the CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write the header row with column names
        writer.writerow([key_name, subkey_name])
        
        # Write the data
        for key, values in dict_1.items():
            for value in values:
                writer.writerow([key, value])

def print_csv_dict_nested_1stlevel(dict_1, key_name, subkey_name, value_name, file_path_name):
    '''
    # DESCRIPTION: prints a nested dictionary to a csv

    # INPUTS:
    dict_1 is a dictionary
    key_name, subkey_name, value_name are strings which are going to be the column header

    # OUTPUTS: a csv with three columns in the order represented
    '''

    # Specify the output CSV file path
    output_file = file_path_name

    # Write the dictionary to the CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write the header row
        writer.writerow([key_name, subkey_name, value_name])
        
        # Write the data from the nested dictionary
        for key, subkey_data in dict_1.items():
            for subkey, values in subkey_data.items():
                for value in values:
                    writer.writerow([key, subkey, value])

def print_csv_dataframe_per_house (grid_houses, house_index,fp_main, fp_3, fp_4, fp_5, fp_6):
    for hs in house_index:
        for l in grid_houses['depths_dataframe'][hs]:
            grid_houses[fp_3][hs][l].to_csv(fp_main + fp_3 + f"_{hs}_{l}.csv", index=None)
            grid_houses[fp_4][hs][l].to_csv(fp_main + fp_4 + f"_{hs}_{l}.csv", index=None)
            grid_houses[fp_5][hs][l].to_csv(fp_main + fp_5 + f"_{hs}_{l}.csv", index=None)
            grid_houses[fp_6][hs][l].to_csv(fp_main + fp_6 + f"_{hs}_{l}.csv", index=None)




# # Specify the file path where you want to save the dictionary
# file_path = "D:\OneDrive - Delft University of Technology\CORE\python files\Script_28_10_2023\grid_houses.pkl"

# # Save the dictionary to a file using Pickle
# with open(file_path, 'wb') as file:
#     pickle.dump(grid_houses, file)




# # Record the end time
# end_time = time.time()
# # Calculate the execution time
# execution_time = end_time - start_time
# print(f"Execution time using time module: {round(execution_time*1000,3)} milliseconds")
