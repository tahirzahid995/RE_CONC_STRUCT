################################       IMPORT DATABASE 2 AS CSV INTO DICTIONARY AND CLEAN    ##########################################
import pandas as pd
import numpy as np
import csv

def lengths_into_groups(dataframe, tolerance):
    lengths = list(dataframe['lengths'])
    # Sort the lengths in ascending order
    lengths.sort()
    
    groups = []
    
    for length in lengths:
        added = False
        for group in groups:
            if abs(length - group[0]) <= tolerance:
                group.append(length)
                added = True
                break
        
        if not added:
            # If no suitable group is found, create a new group
            groups.append([length])
    
   
    total_group_length = 0
    max_group_length = 0
    tolerance_group = tolerance + 0.2
    for group in groups:
        total_group_length += len(group)
        if max_group_length == 0 : 
            max_group_length = len(group)
        elif max_group_length < len(group):
            max_group_length = len(group)
        
    mean_group_length = total_group_length/len(groups)
    
    new_groups = []
    i = 0  # Initialize an index variable

    while i < len(groups):
        group1 = groups[i]
        if i + 1 < len(groups):  # Check if there is another group to merge with
            group2 = groups[i + 1]

            if (
                group1[0] < mean_group_length / 2 and
                group2[0] < mean_group_length and
                group1[0] + group2[0] <= max_group_length and
                abs(min(group1) - max(group2)) < tolerance_group
            ):
                new_group = group1 + group2
                new_groups.append(new_group)
                i += 2  # Move to the next pair of groups
            else:
                new_groups.append(group1)
                new_groups.append(group2)
                i += 2  # Move to the next pair of groups
        else:
            new_groups.append(group1)  # If there's only one group left
            i += 1

# Now new_groups contains the merged groups based on the conditions


    beam_groups = []
    for group in new_groups: 
        unique_group_numbers = list(set(group))
        unique_group_numbers.sort()
        beam_groups.append(unique_group_numbers)   
        
        file_name = "beam_groups.csv"

    # Writing to CSV file in one line
    csv.writer(open(file_name, 'w', newline='')).writerows(beam_groups)
           
    return beam_groups



'''
    # DESCRIPTION: 
    A function that returns a dictionary with different groups of length from the dataframe
    
    
    # INPUTS:
    
    1. A dataframe with a column named 'lengths' containing different numbers 
     
    2. The amount of groups that we want the lengths to be separated to
    
    # OUTPUTS:

        dict_list = {
    'B0':{'ID':'N/A', 'SIZE':0, 'LENGTH':0},
    'B1':{'ID':'various B1 codes', 'SIZE':29, 'LENGTH':1},
    'B2':{'ID':'various B2 codes', 'SIZE':52, 'LENGTH':2},
    'B3':{'ID':'various B3 codes', 'SIZE':122, 'LENGTH':3},
    'B4':{'ID':'various B4 codes', 'SIZE':133, 'LENGTH':4},
    'B5':{'ID':'various B5 codes', 'SIZE':30, 'LENGTH':5}
    } 
    
    axial_combinations = {
        'y' : [['B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1'], 
            ['B2', 'B2', 'B2', 'B2', 'B2']]
        'x' : [['B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1'],
            ['B2', 'B2', 'B2', 'B2', 'B2', 'B2']] 
        }   
        
'''
def dataframe_to_dictionary(dataframe, tolerance):
    
# Create an empty list to hold the dictionaries
    dict_list = {}
    groups_of_lengths = lengths_into_groups(dataframe,tolerance)  
    
    group_number = len(groups_of_lengths)+1      
    for i in range(1,group_number): 
        dict_name = 'B' + str(i)
        dict_list[dict_name] = {}
        group_length = groups_of_lengths[i-1]
        dict_values = dataframe[((dataframe['lengths']) >= min(group_length)) & (dataframe['lengths'] <= max(group_length))]
        # dict_list[dict_name]= {'ID':dict_values}
        dict_list[dict_name]['ID'] = dict_values['IDs'].to_list()  
        dict_list[dict_name]['LENGTH'] = max(group_length)
        dict_list[dict_name]['SIZE'] = len(dict_list[dict_name]['ID'])
        dict_list[dict_name]['DATAFRAME'] = dict_values
    
    new_dict_list = {}
    total_size = 0
    for group_name,group in dict_list.items(): 
        total_size += dict_list[group_name]['SIZE']
    
    average_size = total_size/len(dict_list) 
    for group_name, group in dict_list.items():
        if group['SIZE'] > average_size:
            new_dict_list[group_name] = group   
            
    return new_dict_list 


if __name__ == "__main__":
    # Generate the pickle thing
    print()
