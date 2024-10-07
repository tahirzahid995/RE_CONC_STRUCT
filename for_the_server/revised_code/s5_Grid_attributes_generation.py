################### COMPARE THE GRID BEAM REQUIREMENTS WITH THE DATAFRAME BEAMS ################     

import json
import time
import math





def find_amount_of_houses(list_comb,dict_list):
    '''
            # DESCRIPTION: 
            We compare  the beams of the grid with the B1 amounts of the database. 
            We create a dictionary which contains the name of the grid 
            As keys we place the beam types and as values
            'the amount of this beam type'/ 'total amount of existing beams of the same type'
            
            
            # INPUTS:
            List of possible grid combinations (list_comb), List of available beam types from inventory (dict_list)
            list_comb = {
            'grid_1':{'x':'b1,b1,b1', 
                    'y': 'b3,b3,b3',
                    'group_quantities':{'b1': total amount of b1s needed for grid ,
                                        'b2':total amount of b2s needed for grid}
                    'beams_of_x' = b1,b1,b1* (len(y)+1), 
                    'beams_of_y'= b3,b3,b3*(len(x)+1)
                    }     
                    
            dict_list = {
                'B0':{'ID':'N/A', 'SIZE':0, 'LENGTH':0},
                'B1':{'ID':'various B1 codes', 'SIZE':29, 'LENGTH':1},
                'B2':{'ID':'various B2 codes', 'SIZE':52, 'LENGTH':2},
                'B3':{'ID':'various B3 codes', 'SIZE':122, 'LENGTH':3},
                'B4':{'ID':'various B4 codes', 'SIZE':133, 'LENGTH':4},
                'B5':{'ID':'various B5 codes', 'SIZE':30, 'LENGTH':5}
            } 
            # OUTPUTS:
            dictionary (results)
            result = {
                'grid1': {'B1':0}
                'grid2': {'B1':0
                        'B2':2
                        'B3':1}
            }
            
            '''                
    result = {}  # Initialize an empty result dictionary

    # Iterate through each grid in list_comb
    for each_grid, grid_attributes in list_comb.items():
        #result_key = 'grid ' + each_grid
        result[each_grid] = {}  # Initialize a sub-dictionary for the current grid

        for key, value in grid_attributes['group_quantities'].items():
            if key in dict_list and 'SIZE' in dict_list[key]:
                try:
                    division_result = math.floor(dict_list[key]['SIZE'] / value)
                except ZeroDivisionError:
                    division_result = 0
                result[each_grid][key] = division_result

    # Now, the 'result' dictionary contains the calculated division results.
                    

    '''
        # DESCRIPTION: 
        An extra key is created in results dictionary to show the amount of possible houses
        The amount of possible houses = the smallest value from the keys B1,B2,B3---
        
        # OUTPUTS:
        result = {
            'grid1': {'B1':0
                    'amount_of_houses : 0' }
            'grid2': {'B1':0
                    'B2':2
                    'B3':1}
                    'amount_of_houses : 0'                  
        }

        
        '''                
    '''
        # DESCRIPTION: 
        The total amount of possible houses is calculated by iterating throught all the ['amount_of_houses'] keys and adding the values together 
        
        '''                

    #Store the data into a key called possible_amount_ofhouses
    sum_amount = 0
    new_result = {}
    for each_grid, grid_values in result.items():
        # Use a custom key function to find the minimum value within each grid's values
        min_key = min(grid_values.values())
        grid_values['amount_of_houses'] = math.floor(min_key)
        #if 'amount_of_houses' in each_grid_value:
        amount_houses = min_key
        sum_amount += amount_houses 
        if amount_houses > 0 :
            new_result[each_grid] = grid_values

        
    return(new_result,sum_amount)    


#TODO delete all the zero houses grids before you find the average #DONE
#TODO after finding the amount of houses available, make sure it is not a float and round them to the low integer #DONE

def find_grids_optimized_for_house(dict_list,list_comb,minimum_nohouses) : 
    '''
    # DESCRIPTION: 
    Create a new dictionary that stores the grids where 
    the amount of possible houses exceeds the average amount of houses
    
    # INPUTS:
    Dictionary of possible grid combinations (list_comb), 
    Dictionary of grids with the amounts of beams that they need and the amount of possible houses (result)
    
    list_comb = {
    'grid1':{'x':'b1,b1,b1', 
             'y': 'b3,b3,b3',
             'group_quantities':{'b1': total amount of b1s needed for grid ,
                                 'b2':total amount of b2s needed for grid}
             'beams_of_x' = b1,b1,b1* (len(y)+1), 
             'beams_of_y'= b3,b3,b3*(len(x)+1)
             }     
    
    result = {
        'grid1': {'B1':0
                  'amount_of_houses : 0' }
        'grid2': {'B1':0
                  'B2':2
                  'B3':1}
                  'amount_of_houses : 0'
    }
             
    
    # OUTPUTS:
    
    possible_grids = {
        'grid24': {'amount_of_houses' : '2'
                   'x':'b1,b1,b1', 
                   'y': 'b3,b3,b3',
                   'group_quantities':{'b1': total amount of b1s needed for grid ,
                                       'b2':total amount of b2s needed for grid}
                   'beams_of_x' = b1,b1,b1* (len(y)+1), 
                   'beams_of_y'= b3,b3,b3*(len(x)+1)
    
    }
    
    ''' 
    result,sum_amount = find_amount_of_houses(list_comb=list_comb,dict_list=dict_list)   
    possible_grids = {}            

    average_amount = sum_amount / len(result)  # Calculate the average
    if average_amount < 1:
        average_amount = 1

    possible_grids = {}  # Initialize a dictionary to store possible grids

    for each_grid, each_grid_value in result.items():
        # Check if 'amount_of_houses' is a key in each_grid_value
        if 'amount_of_houses' in each_grid_value:
            amount = each_grid_value['amount_of_houses']  # Access the value
            if amount > average_amount or amount >= minimum_nohouses:
                possible_grids[each_grid] = list_comb[each_grid]
                possible_grids[each_grid]['amount_ofhouse'] = amount

    # Now, possible_grids contains the grids with 'amount_of_houses' values greater than the average


    # store the amount of columns of each grid
    for grid in possible_grids:
        possible_grids[grid]['no.Columns'] = (len(possible_grids[grid]['x'])+1) * len(possible_grids[grid]['y'])

    #Give the houses with the least amount of columns
    sum_amount_columns = 0
    
    for each_grid,value in possible_grids.items(): 
        amount_columns = value['no.Columns']
        sum_amount_columns += amount_columns  

    average_amount_columns = sum_amount_columns / len(possible_grids)  # Calculate the average
    if average_amount_columns < 1:
        average_amount_columns = 1
        
    possible_newgrids = {}  # Initialize a dictionary to store possible grids

    for each_grid, each_grid_value in possible_grids.items():
        # Check if 'amount_of_houses' is a key in each_grid_value
        if 'no.Columns' in each_grid_value:
            amount = each_grid_value['no.Columns']  # Access the value
            if amount >= average_amount_columns:
                possible_newgrids[each_grid] = possible_grids[each_grid]

    possible_grids = possible_newgrids
    return possible_grids
    

