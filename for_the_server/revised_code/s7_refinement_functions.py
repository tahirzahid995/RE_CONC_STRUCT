import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import copy
import time
import math



'''# Record the start time
start_time = time.time()

print('\n','---this code: REFINEMENT FUNCTIONS starts here---','\n')'''


########################################   FUNCTIONS FOR REFINEMENT AFTER STATIC ANALYSIS   ########################


def remove_repetitions_across_keys(x):
    '''
    # DESCRIPTION: removes repetitions across different keys of a dictionary. All unique values are found. A new 
    empty dictionary is made. Then, one by one, each unqiue value is put inside each key in the order
    of the smallest key length to the largest one. If the unique value was not present inside the original key,
    then the other keys are checked.

    This works well for a large number of values more or less evenly distributed in the keys of the input. 
    This does not work very well for optimized selection. 
    To do that value(2) should be checked if it can be assigned to a smaller(in length) key. However, this would 
    mean each time all the values have been assigned once, the loop should continue from value(2) so it can be
    assigned to A. Alternatively, the function can be programmed as an optimization function where 1 house is made
    when all keys have been assigned a value once; the objective function would need to be maximized in this case.

    # INPUT: 
    x = {'A': [1,2,3], 'B': [1,2,3,4,5,6,7,8,9], 'C': [1,2,3,4,5,6,7,8], 'D': [1,2,3,4,5,6,7,8,9,10]}

    # OUTPUT:
    {'A': [1], 'B': [3, 7, 9], 'C': [2, 5, 6], 'D': [4, 8, 10]}

    # PROCESS:
        unique_list = [1,2,3,4,5,6,7,8,9,10]
        order = [A,C,B,D]
    Does A have 1? Yes, Then add to A.
    Does C have 2? Yes, Then add to C.
    Does B have 3? Yes, Then add to B.
    Does D have 4? Yes, Then add to D.
    Does A have 5? No, Then check if any other key has it in the order [A,C,B,D]
    '''

    # unique list
    unique_list = []
    for key in x.keys():
        for i in x[key]:
            if i not in unique_list:
                unique_list.append(i)
    # print(f"unique_list is {unique_list}")


    # number of values in each key
    lengths = [len(i) for i in x.values()]
    # print(f"lengths is {lengths}")
    

    # the order of keys according to number of values (shortest to largest)
    order = [list(x.keys())[i] for i in np.argsort(lengths)]
    # print(f"order is {order}")


    # order of key repeats till len (unique_values)
    order_rep =[]
    while len(order_rep) < len(unique_list):
        order_rep += order
    order_rep[:len(unique_list)]
    # print(f"order_rep is {order_rep}")


    # making a new dictionary with the same keys as the original
    x_new={}
    for key in x:
        x_new[key]=[]
        l = list(x_new[key])

    '''
    ALTERNATIVE SCRIPT

    # original shortest list always gets priority
    # cons: doesn't work if all keys have equal length
    for val in unique_list:
        key_shortest = order[0]
        for key in order:
            if val in x[key]:
                x_new[key].append(val)
                break
    '''



    # each unique value is checked if it can be put one by one into the key 
    # (ordered according to shortest to longest orginal order)
    # cons:  the values of the smallest list may get distributed in others

    unique_list_copy = copy.deepcopy(unique_list)

    # looping through each key and unique value
    for val,key in zip(unique_list,order_rep):
        # key_shortest = order[0]
        
        # # skip if value can be assigned to the shortest key (and this key is not that)
        # if val in x[key_shortest] and key != key_shortest:
        #     val_skip = val
        #     pass
    
    # is value in the original key? then add in the new one
    # else: 
        if val in x[key]:
            x_new[key].append(val)


        # otherwise check the other key( order of checking is original ascending order)
        else:
            # index order
            for i in np.argsort(lengths):
                # alternative key
                key_alt = list(x.keys())[i]
                if val in x[key_alt]:
                    x_new[key_alt].append(val)
                    break

        # delete the appended value from the unique list (copy) so these values can be added to the shorter keys        
        del unique_list_copy[unique_list_copy.index(val)]

    # checking if the number of values in the new dictionary are the same as the original one
    unique_sum= sum([len(i) for i in x_new.values()])
    if len(unique_list) != unique_sum:
        print('\n', f'{len(unique_list) - unique_sum} VALUES ARE MISSING','\n')
    
    return(x_new)






def add_suffix_to_key(x, suffix):
    '''
    # DESCRIPTION : adds a suffix to the names of all keys in the dictionary
    
    # INPUTS: a dictionary (x) and a string (suffix)
    x = {'A': [1,2,3], 'B': [1, 2,3,4,5,6,7,8,9], 'C': [1,2,3,4,5,6,7,8], 'D': [1,2,3,4,5,6,7,8,9,10]}
    suffix = x

    # OUTPUTS: 
    dictionary = {'Ax': [1,2,3], 'Bx': [1, 2,3,4,5,6,7,8,9], 'Cx': [1,2,3,4,5,6,7,8], 'Dx': [1,2,3,4,5,6,7,8,9,10]}
    '''


    x_suffix = {}
    for key,val in x.items():
        x_suffix[str(key) + suffix] = val
    return(x_suffix)




def merge_nested_dicts(dict1, dict2):
    '''
    # DESCRIPTION: merges two nested dictionaries together. if the nested key (y in this case) repeats too. 
    then the value of dict2 replaces dict1

    # INPUTS:
    dict1 = {'a': 1, 'b': {'x': 2, 'y': 3}}
    dict2 = {'b': {'y': 4, 'z': 5}, 'c': 6}
    
    # OUTPUTS:
    {'a': 1, 'b': {'x': 2, 'y': 4, 'z': 5}, 'c': 6}
    '''
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            # If both values are dictionaries, recursively merge them
            dict1[key] = merge_nested_dicts(dict1[key], dict2[key])
        else:
            # If the key is not in dict1 or the values are not both dictionaries, update the value
            dict1[key] = dict2[key]
    return dict1




def merge_double_nested_dicts(grid):
    '''
    # DESCRIPTION: Merges a doubly nested dictionary. USeful if there is a dictionary (grid) and the subkeys ('B4')
    are to be merged such that the sub-subkeys (4.0) are kept as separate keys. so one in x, the sub-subkeys (4.0)
    are given a unique name (4.0x and 4.0y) which is a concantenation of the sub-subkey(4.0) and the key(x)

    # INPUTS:
    grid = {'x': {'B4': {4.0: [1,2,3,4], 7.0: [1,2,3,4,5,6,7,8], 6.75: [1,2,3,4,5,6]}, 
        'B2': {4.0: [10,20,30,40], 7.0: [10,20,30,40,50,60,70,80], 6.75: [10,20,30,40,50,60]}}, 
        'y': {'B4': {4.0: [1,2,3,4], 7.0: [1,2,3,4,5,6,7,8], 6.75: [1,2,3,4,5,6]}}}

    # OUTPUTS:
    {'B4': {'4.0x': [1, 2, 3, 4], '7.0x': [1, 2, 3, 4, 5, 6, 7, 8], '6.75x': [1, 2, 3, 4, 5, 6], 
           '4.0y': [1, 2, 3, 4], '7.0y': [1, 2, 3, 4, 5, 6, 7, 8], '6.75y': [1, 2, 3, 4, 5, 6]}, 
    'B2': {'4.0x': [10, 20, 30, 40], '7.0x': [10, 20, 30, 40, 50, 60, 70, 80], '6.75x': [10, 20, 30, 40, 50, 60]}}
    '''

    grid_merge ={}
    for key, val in grid.items():
        l = key
        for beam_type in grid[l]:
            beam_type_dic = grid[l][beam_type]
            beam_type_dic_new = add_suffix_to_key(beam_type_dic,l)
            if beam_type in grid_merge.keys():
                dic_dummy={}
                dic_dummy[beam_type] = beam_type_dic_new
                # print(dic_dummy)
                # print(grid_merge)
                grid_merge = merge_nested_dicts(grid_merge,dic_dummy)
            else:
                grid_merge[beam_type]= beam_type_dic_new
            # print(beam_type)
            # print('---')
    return grid_merge




###############################################   FUNCTIONS  FOR S9  #############################################


def sort_dataframe_by_column(dataframe, column_name):
    '''
    # DESCRIPTION: sorts a dataframe according to the values of the column

    # INPUTS: 
    dataframe with column ('IDs')
    columnn name to be sorted by

    # OUTPUTS: a dictionary where the sorted IDs are the key and the value is the order
    {'ID_2296': 0, 'ID_4494': 1, 'ID_5577': 2, 'ID_9741': 3, 'ID_1028': 4, 'ID_4384': 5, 'ID_4810': 6}
    '''
    # all sorted ids of the dataframe
    sorted_df = list(dataframe.sort_values(by= column_name)['IDs'])
    # dictionary of sorted ids
    position_dict = {value: idx for idx, value in enumerate(sorted_df)}
    return position_dict    


def sort_dataframe_by_columnA_whilst_refining_by_columnB(dataframe, column_name_A, column_name_B, values_B):
    '''
    # DESCRIPTION: sorts a dataframe according to the values of the column A that has already been
    refined according to values B in column B
     
    # INPUTS: 
    dataframe with column ('IDs')
    column name A to be sorted by. eg 'weight'
    column name B to refine the dataframe by. eg 'Warehouse' 
    values B to refined the dataframe by. it is a list.eg ['Warehouse_1'] or ['Warehouse_1',['Warehouse_2']] 

    # OUTPUTS: a dictionary where the sorted IDs are the key and the value is the order
    {'ID_2296': 0, 'ID_4494': 1, 'ID_5577': 2, 'ID_9741': 3, 'ID_1028': 4, 'ID_4384': 5, 'ID_4810': 6}
    '''

    # filtering the dataframe
    filtered_dataframe = dataframe[dataframe[column_name_B].isin(values_B)]
    # all sorted ids of the dataframe
    sorted_df = list(filtered_dataframe.sort_values(by= column_name_A)['IDs'])
    # dictionary of sorted ids
    position_dict = {value: idx for idx, value in enumerate(sorted_df)}
    return position_dict    


def sort_nested_dic_acc_to_dataframe_column_1(IDs, dataframe ):
    '''
    # DESCRIPTION: it sorts a list according to a column in a dataframe.

    # INPUTS: 
    IDs = [24, 59, 74, 246, 280, 339, 376, 446, 502, 520, 555, 615, 656, 706, 893, 907, 954, 1044, 1058]
        24, 59, 74 etc are beam IDs for tributary areas 2.25 etc in a beam type (B3)

    Dataframe is a dataframe with a column named 'IDs'

    # OUTPUTS:
    [893, 954, 615, 520, 280, 24, 446, 706, 502, 59, 1058, 1044, 907, 376, 656, 339, 74, 246, 555]
    The ids are sorted according to the weights (ascending order) as designated by the dataframe
    '''
    # all sorted ids of the dataframe
    sorted_df = list(dataframe.sort_values(by='weight')['IDs'])
    # dictionary of sorted ids
    position_dict = {value: idx for idx, value in enumerate(sorted_df)}
    # sorting the list according to the positions in the dictionary
    sorted_id_for_each_area = sorted(IDs, key= position_dict.get)

    return sorted_id_for_each_area


def sort_nested_dic_acc_to_dataframe_column_2(IDs, dict_position_of_dataframe ):

    '''
    # DESCRIPTION: it sorts a list according to a column in a dataframe.

    # INPUTS: 
    IDs = [24, 59, 74, 246, 280, 339, 376, 446, 502, 520, 555, 615, 656, 706, 893, 907, 954, 1044, 1058]
        24, 59, 74 etc are beam IDs for tributary areas 2.25 etc in a beam type (B3)

    dict_position_of_dataframe is a dictionary where the sorted IDs are the key and the value is the order.
    Output from sort_dataframe_by_column function

    # OUTPUTS:
    [893, 954, 615, 520, 280, 24, 446, 706, 502, 59, 1058, 1044, 907, 376, 656, 339, 74, 246, 555]
    The ids are sorted according to the weights (ascending order) as designated by the dataframe
    '''
    # removing variables that are not in the dictionary
    IDs = [i for i in IDs if i in dict_position_of_dataframe]

    # sorting the list according to the positions in the dictionary
    sorted_id_for_each_area = sorted(IDs, key= dict_position_of_dataframe.get)

    return sorted_id_for_each_area


def filter_dictionary(dictionary, num_of_keys):
    '''
    # DESCRIPTION: gives a filtered dictionary with the first number of keys as specified by num_of_keys

    # INPUT: a dictionary and an integer 
    
    # OUTPUT: the filtered dict with first num_of_keys
    '''
    filtered_dict = {}
    keys_to_keep = list(dictionary.keys())[:num_of_keys]

    for key in keys_to_keep:
        if key in dictionary:
            filtered_dict[key] = dictionary[key]

    return filtered_dict

def haversine_distance(lat1, lon1, lat2, lon2):
    '''
    # DESCRIPTION: calculates the distance between two locations on Earth
    # INPUT: coordinates of two locations (latitude, longitude)
    # OUTPUT: DISTANCE in km
    '''
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    radius_of_earth = 6371  # Radius of the Earth in kilometers
    distance = round(radius_of_earth * c,1)

    return distance


###############################################   SAMPLE TEST DATA   #############################################

'''print('---PRINTING CODE: REFINEMENT FUNCTIONS STARTS HERE---')

# x is B1 from x beams
xxx = {'A': [1,2,3], 'B': [1, 2,3,4,5,6,7,8,9], 'C': [1,2,3,4,5,6,7,8], 'D': [1,2,3,4,5,6,7,8,9,10]}

# y is B1 from y beams
y = {'A': [1,2,3], 'E': [1,2,3,4,5,6,7,8,9,10,11,12,13,14]}


# Sample grid
grid = {'x': {'B4': {4.0: [1,2,3,4], 7.0: [1,2,3,4,5,6,7,8], 6.75: [1,2,3,4,5,6]}, 
       'B2': {4.0: [10,20,30,40], 7.0: [10,20,30,40,50,60,70,80], 6.75: [10,20,30,40,50,60]}}, 
'y': {'B4': {4.0: [1,2,3,4], 7.0: [1,2,3,4,5,6,7,8], 6.75: [1,2,3,4,5,6]}}}


# Example dictionaries with nested structure
dict1 = {'a': 1, 'b': {'x': 2, 'y': 3}}
dict2 = {'b': {'y': 4, 'z': 5}, 'c': 6}

# merged_dict = merge_nested_dicts(dict1, dict2)
# print(merged_dict)
# print('---')       
# print(merge_double_nested_dicts(grid))
# print(remove_repetitions_across_keys(xxx))



# Record the end time
end_time = time.time()
# Calculate the execution time
execution_time = end_time - start_time
print(f"Execution time using time module: {round(execution_time*1000,3)} milliseconds")
'''
