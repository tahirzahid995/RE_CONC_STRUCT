import pandas as pd
import numpy as np

import time

from pickle_commands import dump_into_pickle,pickle_open

# possible_grids = pickle_open(file_path='C:\\Codes\\Core\\OneDrive_1_28-10-2023\\revised_code\\possible_grids.pkl')
# dict_list = pickle_open(file_path='C:\\Codes\\Core\\OneDrive_1_28-10-2023\\revised_code\\dict_list.pkl')
#######################################################    FUNCTIONS        ##############################################


# Grid generation

def generate_grid(x_beams,y_beams):
    '''
    # DESCRIPTION: generates a grid from x and y
    Could be useful for visualization of gridsquares

    # INPUTS: x is a list of beams e.g[B1,B2,B2,B3], y is a list of beams e.g[B3,B4,B2,B3,B5,B1]
    '''
    grid=[]
    for y in y_beams:
        row=[]
        for x in x_beams:
            cell= x,y
            row.append(cell)
        grid.append(row)
    return grid





# Grid-area generation

def generate_grid_areas(grid,dictionary):
    '''
    This won't be necessary for algorithm - may be useful for something else later

    # DESCRIPTION: gives the areas of the grid 

    # INPUT: output grid from grid generation function and a dictionary of beam groups with the length of the group
    being a value of key 'LENGTH'
    '''
    grid_areas=[]
    for row in grid:
        grid_areas_row = []
        for bay in row: 
            area= dictionary[bay[0]]['LENGTH']*dictionary[bay[1]]['LENGTH']
            # print(f"area is {area}")
            grid_areas_row.append(area)
        grid_areas.append(grid_areas_row)
    return grid_areas

# print(f"grid areas are {generate_grid_areas(grid_1,beam_dict)}")





# Tributary loading area on beams in x

def tributary_areas_x(x, y, beam_dict, column_width):
    
    '''
    # DESCRIPTION:
    this is for perpendicular beams
    Only gives tributary areas on beams in x. For y, you have to rerun the function and replace the order of inputs
    This may also be useful for visualization purposes to see which different beam is needed where in the grid.

    # INPUTS:
    x = [A,B,C] x is a list of beams. e.g [B1,B2,B3]
    y = [D,E,F,G] y is a list of beams e.g [B4,B5,B2,B1]
    column_width is the width and depth of a square cross_section column

    beam_dict = {
    'B0':{'ID':'N/A', 'SIZE':0, 'LENGTH':0},
    'B1':{'ID':'various B1 codes', 'SIZE':29, 'LENGTH':1},
    'B2':{'ID':'various B2 codes', 'SIZE':52, 'LENGTH':2},
    'B3':{'ID':'various B3 codes', 'SIZE':122, 'LENGTH':3},
    'B4':{'ID':'various B4 codes', 'SIZE':133, 'LENGTH':4},
    'B5':{'ID':'various B5 codes', 'SIZE':30, 'LENGTH':5}
    } 
    beam_dict is a dictionary with lengths stored as values of a key which refer to the beams in x and y

    # OUTPUTS:
    gives the tributary areas in the form of a dataframe
    '''
    
    # tribarea = []
    # X = [beam_list_1,beam_list_2]
    # Y = [beam_list_2,beam_list_1]
    # for x,y in X,Y:

    beam_load_x_all = []
    for i, beam_x in enumerate(x):
        beam_load_x_each = []
        z = ['B0'] + y + ['B0']
        for j in range(len(z)-1):
            # x1 is the beam for which the area is being calculated
            # y1 is the beam which makes make the grid rectangle
            
            # for y1
            if j == 1 or j == len(y):
                y1 = beam_dict[z[j]]['LENGTH'] + 1.5*column_width
            else:
                y1= beam_dict[z[j]]['LENGTH'] + column_width

            # for y2    
            if j+1 == 1 or j+1 == len(y):
                y2 = beam_dict[z[j+1]]['LENGTH'] + 1.5*column_width
            else:
                y2= beam_dict[z[j+1]]['LENGTH'] + column_width

            # for x1
            if i == 0 or i == len(x)-1:
                x1 = beam_dict[x[i]]['LENGTH'] + 1.5*column_width
            else:
                x1 = beam_dict[x[i]]['LENGTH'] + column_width
            
    
            # first area from y1 on x1       

            # triangular area (in  a rectangle)
            if x1 < y1:
                beam_load_xy1 = x1**2/4
            # trapezoidal area (in  a rectangle)
            elif x1 > y1:
                beam_load_xy1 = (y1/4)*(2*x1-y1)
                if y1 == column_width:
                    beam_load_xy1 = 0
            # triangular area (in a square)
            elif x1 == y1:
                beam_load_xy1 = x1*y1/4 
    

            # second area from y2 on x1       

            # triangular area (in  a rectangle)
            if x1 < y2:
                beam_load_xy2 = x1**2/4
            # trapezoidal area (in  a rectangle)
            elif x1 > y2:
                beam_load_xy2 = (y2/4)*(2*x1-y2)
                if y2 == column_width:
                    beam_load_xy2 = 0                
            # triangular area (in a square)
            elif x1 == y2:
                beam_load_xy2 = x1*y2/4 

            # total area on one beam
            beam_load_x = round(float(beam_load_xy1 + beam_load_xy2),2)
    
            # total area on each beam of x
            beam_load_x_each.append(beam_load_x)
        # total area on each beam of x
        beam_load_x_all.append(beam_load_x_each)
    # return beam_load_x_all



    # Assigning a key to the loading area on x_beams
    '''
    The alphabet is only an indicator of the position of a beam
    '''
    alphabet = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

    x_areas = pd.DataFrame()
    for i, col_names in enumerate(x):
        x_areas[f"{alphabet[i]}-{x[i]}"] = beam_load_x_all[i]

    return x_areas
    

# Quantities of the Tributary loading areas in x with respect to its x-position

def tributary_areas_x_qty_by_position(areas):
    '''
    # DESCRIPTION: processes a dataframe into a dictionary that shows how many instances of the same tributary 
    area exist in the beam position (A,B,C) 
    This may also be useful in case the number of unique tributary areas are required specific to each beam position.
   
    # INPUTS : areas is a dataframe which has the tributary loading areas on beams in x or y. The columns
    are for e.g A-B1, B-B2, C-B2, D-B3 while the rows are tributary areas. It is the ouptut you get 
    from the tributary_areas_x function. An example is shown below.
    
        A-B4  B-B2  C-B2
    0  3.75  2.25  2.25
    1  7.75  6.25  6.25
    2  8.00  8.00  8.00
    3  8.00  8.00  8.00
    4  7.75  6.25  6.25
    5  3.75  2.25  2.25

    # OUTPUTS: An example is shown below.

    {'A-B4': {3.75: 2, 7.75: 2, 8.0: 2}, 'B-B2': {2.25: 2, 6.25: 2, 8.0: 2}, 'C-B2': {2.25: 2, 6.25: 2, 8.0: 2}}'

    '''
    # Identifying unique loading areas and repetitions 
    x_areas_unique={}
    for i, col_names in enumerate(areas.columns):
        unique_values = list(np.round(areas[col_names].unique(),2))
        counts = areas[col_names].value_counts()

        x_areas_unique[col_names] = {}
        for value, count in zip(unique_values, counts):
            x_areas_unique[col_names][value] = count

        # print(f"unique_values is {unique_values}")
        # print(f"count list is {x_areas_unique}")
        # print('---') 
    return x_areas_unique




# Quantities of the Tributary loading areas in x regardless of any position

def tributary_areas_x_qty_by_length(trib_dict):
    '''
    # DESCRIPTION: merges a dictionary and shows how many instances of the same beam tributary area exist
    depending on the beam group (e.g B1,B2,B3) regardless of beam position (e.g A,B,C,D).

    It checks the keys in which the last two characters of the keys repeat (for e.g in A-B1 and and C-B1, B1 repeats)
    this is so we can merge the same beam groups together, and then update the unique tributary areas as well as the 
    count of repetitions found). So whether or not A-B1 and C-B1, contain the same or have any unique tributary areas, 
    it will get updated.

    # INPUTS: trib_dict is a dictionary of unique tributary areas
    e.g: {'A-B4': {3.75: 2, 7.75: 2, 8.0: 2}, 'B-B2': {2.25: 2, 6.25: 2, 10.0: 2}, 'C-B2': {2.25: 2, 6.25: 2, 8.0: 2}}'

    # OUTPUTS: returns the refined dictionary with merged keys
    e.g: {'B4': {3.75: 2, 7.75: 2, 8.0: 2}, 'B2': {2.25: 4, 6.25: 4, 10.0: 2, 8.0: 2}}
    '''
    refined_dict = {}  # Dictionary to store keys with the same last two characters

    for key, value in trib_dict.items():
        last_chars = key[2:]
        if last_chars in refined_dict:
            # If last two characters repeat, merge the values
            for subkey, subvalue in value.items():
                if subkey in refined_dict[last_chars]:
                    refined_dict[last_chars][subkey] += subvalue
                else:
                    refined_dict[last_chars][subkey] = subvalue
        else:
            refined_dict[last_chars] = value

    return refined_dict

#####################################################   INPUTS     #####################################################
'''



# # Sample Beam dictionary - placeholder for nefeli's dictionary
# beam_dict_1 = {
#     'B0':{'ID':'N/A', 'SIZE':0, 'LENGTH':0},
#     'B1':{'ID':'various B1 codes', 'SIZE':29, 'LENGTH':1},
#     'B2':{'ID':'various B2 codes', 'SIZE':52, 'LENGTH':2},
#     'B3':{'ID':'various B3 codes', 'SIZE':122, 'LENGTH':3},
#     'B4':{'ID':'various B4 codes', 'SIZE':133, 'LENGTH':4},
#     'B5':{'ID':'various B5 codes', 'SIZE':30, 'LENGTH':5}
# }

# # Sample Grid - plaeholder for nefeli's grid list
# grid_list_of_beams = [
#     [['B4','B2','B2'],['B4','B2','B3','B5','B1']], 
#     [['B4','B3','B1','B4','B5'],['B4','B2','B3','B1']], 
#     [['B5','B2','B4','B1','B1'],['B5','B5','B2','B1','B2','B2']]]
# # Labelling the list of grids into a dictionary
# grid_dict_of_beams={}
# for i, grid in enumerate(grid_list_of_beams):
#     grid_dict_of_beams[f'grid_{i}'] = grid




# # nefeli's dictionary
# beam_dict_1 = dict_list
# beam_dict_1['B0'] = {}
# beam_dict_1['B0'] = {'ID':'N/A', 'SIZE':0, 'LENGTH':0}


# # nefeli's grids
# grid_dict_of_beams = {}
# for grid,val in possible_grids.items():
#     grid_dict_of_beams[grid] = {}
#     grid_dict_of_beams[grid] = [possible_grids[grid]['x']] + [possible_grids[grid]['y']]

'''

#######################################################   SOLUTION     ###################################################

def tributary_load_area(possible_grids,dict_list,column_size):
    # importing possible grids
    grid_dict_of_beams = {}
    for grid,val in possible_grids.items():
        grid_dict_of_beams[grid] = {}
        grid_dict_of_beams[grid] = [possible_grids[grid]['x']] + [possible_grids[grid]['y']]
        
    # nefeli's dictionary
    beam_dict_1 = dict_list
    beam_dict_1['B0'] = {}
    beam_dict_1['B0'] = {'ID':'N/A', 'SIZE':0, 'LENGTH':0}

    # Making the master grid 

    grid_master = {}
    for grid in grid_dict_of_beams:
        xx = grid_dict_of_beams[grid][0]
        yy = grid_dict_of_beams[grid][1]

        # Label for keys in the dictionary
        labels = ['x','y']

        # for running the script to solve for x and y separately
        run_x = [xx,yy]
        run_y = [yy,xx]

        # keys of the grid dictionary
        grid_master[grid] = {}
        grid_master[grid]['beams']={}
        grid_master[grid]['tr_area']={}
        grid_master[grid]['tra_qty_pos_req']={}
        grid_master[grid]['tra_qty_req']={}


        for l,x,y in zip(labels,run_x,run_y):

            # Tributary loading area on beams in x or y
            trib_areas = tributary_areas_x(x,y,beam_dict_1,column_size)

            # Quantities of the Tributary loading areas in x (or y) with respect to its x-position (or y-position)
            trib_areas_qty_pos = tributary_areas_x_qty_by_position(trib_areas)

            # Quantities of the Tributary loading areas in x or y regardless of any position
            trib_areas_qty = tributary_areas_x_qty_by_length(trib_areas_qty_pos)


            grid_master[grid]['beams'][l] = x #list
            grid_master[grid]['tr_area'][l] = trib_areas #dataframe
            grid_master[grid]['tra_qty_pos_req'][l] = trib_areas_qty_pos #dictionary
            grid_master[grid]['tra_qty_req'][l] = trib_areas_qty #dictionary
    return grid_master

''' 
The grid_master dictionary key order is: 

1) grid_number: 'grid_0', 'grid_1','grid_2' etc

2) type of data: 

    a) 'beams' 
        List of beams in x or y. list.

    b) 'tr_area' 
        Tributary loading area on beams in x or y. Dataframe.

    c) 'tra_qty_pos_req' 

    d) 'tra_qty_req'
        Required number of beams for 1 house for each area. Dictionary.

    e) 'tra_id_avail' (added later in static analysis part)
        All unrefined possible ids of beams in x or y. Dictionary.

    f) 'tra_qty_avail' (added later in static analysis part)
        All unrefined possible quantities of beams in x or y. Dictionary.

    g) 'tra_id_avail_ref_xy'(added later in static analysis part)
        All refined possible ids of beams in x and y both in one dictionary. Dictionary.

    h) 'tra_qty_avail_ref_xy'(added later in static analysis part)
        All refined possible quantites of beams in x and y both in one dictionary. Dictionary.

`   i) 'tra_id_avail_ref' (added later in static analysis part) 
        All refined possible ids of beams in x or y separately. Dictionary. 

    j) 'tra_qty_avail_ref' (added later in static analysis part) 
        All refined possible quantites of beams in x or y separately. Dictionary. 

    k) 'tra_id_avail_ref_wtsorted'(added later in self weight part)
        Lightest ids of beams in x or y. Dictionary.

    l) 'tra_qty_avail_ref_wtsorted' (added later in self weight part)
        Lightest quantities of beams in x or y. Dictionary.

    m) 'weight' (added later in self weight part)
        Weight of the grid. 1 key gives total weight for all houses. 1 key gives weight per house. Dictionary.

    n) 'missing_beams' (added later in self weight part)
        Quantity of beams for each tributary area that are not satisfied by the stock. . Dictionary.

    o) 'tra_qty_req_h' (added later in self weight part)
        Required number of beams for a given number (h) of houses for each area. Dictionary.
     

3) x or y axis: this is true for all except g,h, and m

'''

##############################################      TESTING MAIN DATA  ###############################################
'''
grid_master = tributary_load_area(possible_grids=possible_grids, dict_list=dict_list)

print('---PRINTING CODE: TRIBUTARY LOAD AREA STARTS HERE---')
# print(grid_master['grid_0']['tra_qty_req']['x'])
# print(grid_master['grid_0'].keys())

grid_to_test = list(grid_master.keys())[2]
print(grid_to_test)
print(grid_master[grid_to_test]['beams'])
print(grid_master[grid_to_test]['tr_area']['x'])
print(grid_master[grid_to_test]['tra_qty_pos_req']['x'])
'''

##############################################    TESTING SAMPLE DATA    ################################################
# y_axis= ['B5','B4','B3','B3','B4','B5']
# x_axis= ['B3','B4','B4','B3']

# y_axis_1= ['B3','B5','B4','B3','B5','B4']
# x_axis_1= ['B4','B3','B4','B3']

# print('---')
# print(tributary_areas_x(y_axis,x_axis,beam_dict_1))
# print('---------------------')
# print(tributary_areas_x(y_axis_1,x_axis_1,beam_dict_1))
# print(tributary_areas_x(x_axis,y_axis,beam_dict_1))
# print(grid_dict_of_beams)






