################################CREATE POSSIBLE 2D GRIDS###########################
import json
import time

'''
    # DESCRIPTION: 
    We compare  the beams of the grid with the B1 amounts of the database. 
    We create a dictionary which contains the name of the grid 
    As keys we place the beam types and as values
    'the amount of this beam type'/ 'total amount of existing beams of the same type'
    
    
    # INPUTS:
    A dictionary with the possible beam combinations for the said length of each axis
                
    axial_combinations = {
    'y' : [['B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1'], 
           ['B2', 'B2', 'B2', 'B2', 'B2']]
    'x' : [['B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1'],
           ['B2', 'B2', 'B2', 'B2', 'B2', 'B2']] 
    } 
    
    # OUTPUTS:
    
    A dictionary of possible grids,the total amount of beam types acting in each axis, the quantities needed of each beam type  
    list_comb = {
    'grid_1':{'x':'b1,b1,b1', 
             'y':'b3,b3,b3',
             'group_quantities':{'b1': total amount of b1s needed for grid ,
                                 'b2':total amount of b2s needed for grid}
             'beams_of_x' = b1,b1,b1* (len(y)+1), 
             'beams_of_y'= b3,b3,b3*(len(x)+1)
             }     
    }
    
'''

#make grid combinations between the two keys
def make_grid_combinations(axial_combinations_dictionary):
    list_comb = {}
    number = 0
    for x_value in axial_combinations_dictionary['x']:
        #print(x_value)
        for y_value in axial_combinations_dictionary['y']:
            #print(y_value)
            grid = {}
            number += 1
            grid ['x'] = x_value
            grid ['y'] = y_value
            grid ['beams_of_x'] = x_value * (len(grid['y']) + 1)
            grid ['beams_of_y'] = y_value * (len(grid['x']) + 1)
            grid ['group_quantities'] = {}
            selected_keys = ['beams_of_x','beams_of_y']
            #list_x = grid['x']
            for selected_key in selected_keys:
                for nested_list in grid[selected_key]:
                    # for value in nested_list: 
                    if nested_list in grid['group_quantities']:
                        # Increment the count if the value is already in the grid
                        grid['group_quantities'][nested_list] +=1
                    else:
                        # Initialize the count to 1 if the value is not in the grid
                        grid['group_quantities'][nested_list]= 1
                list_comb[f'grid_{number}'] = grid
    return list_comb
