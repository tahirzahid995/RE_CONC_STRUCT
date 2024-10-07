import pandas as pd
import numpy as np
import time
import json
import pickle
import os
import pprint
import math

### This should be called from the "for the server/revised_code directory"

#########################################################   INPUTS  #################################################################
# Directory specified by user to save output files
folder_path_user =  os.path.join(os.getcwd(), "outputs")

# Directory for accessing the database and markers of the map. This may be on a server
folder_path_server = os.path.dirname(os.path.realpath(__file__))

# Record the start time
start_time = time.time()
pp = pprint.PrettyPrinter()

print('---')
print('--------------------------------------------------WELCOME TO RE_CONC_STRUCT--------------------------------------------------')
print('-------------The tool that generates concrete structures for mass housing using reusing existing concrete stock--------------')
print('---')


# Read the DataFrame from your source, for example, a CSV file
df = pd.read_csv(os.path.join(folder_path_server, 'Dataframe2.csv'))

# Inputs prompted for the user

# user_input = input('Place required number of houses here: (eg to choose 68 houses, type "68")')
# print(f"Required number of houses is {user_input}")
minimum_nohouses =  68 # int(user_input)
print('---')
# if minimum_nohouses < 5 : 
#     print('This amount is less than the possible limit')

print("------------------Let's specify the location of your houses------------------")
print('---')
# user_input = input('Enter latitude and longitude: (eg for a particualar location in Kahramanmaras, Turkey, type "37.5419,36.8324"')
lat_1, lon_1 = 37.5419,36.8324
print(f"The location is {lat_1} , {lon_1}")
print('---')

print("------------------Let's specify the footprint of your houses------------------")
print('---')
# user_input = input('Please specify x dimension in metres: (eg to choose 10 metres type "10")')
# print(f"x dimension is {user_input} metres")
x_axis_length = 10 #int(user_input)
print('---')

# user_input = input('Please specify y dimension in metres: (eg to choose 20 metres type "20")')
# print(f"y dimension is {user_input} metres")
y_axis_length = 20# int(user_input)
print('---')

# user_input = input('Please specify tolerance for deviation from given dimensions in metres: (eg to choose 1 metres type "1")')
# print(f"tolerance is {user_input} metres")
axis_tolerance = 1.0 #float(user_input)
print('---')


# Inputs may be changed manually

# y_axis_length = 20
# axis_tolerance = 1
column_size = 0.6
my_tolerance = 0.1

# density of concrete
p_conc = 2400
# depth of the concrete slab
d_conc = 0.2
# weight a truck can carry in N
weight_per_truck = 10*1000*9.81
# objectives to optimize
Obj_1 = 'distance'
Obj_2 = 'weight'    




#################################################   EXPORTING  ###################################################

'''
# The following keys have not been exported to folder:

1) beams
2) distance

'''
# print('---')
# user_input = input('Place file-path to download excel sheets of your houses: (eg "D:/OneDrive - Delft University of Technology/CORE/python files/final_csv_set')
# fp_main  = str(user_input)

# Specify the file paths for CSV set

fp_main=os.path.join(folder_path_user,'csv_set/')
if not os.path.exists(fp_main):
    os.makedirs(fp_main)

fp_1 = 'ids_per_warehouse.csv'
fp_2 = 'weight_per_house.csv'
fp_3 = 'depths_dataframe'
fp_4 = 'lengths_dataframe'
fp_5 = 'widths_dataframe'
fp_6 = 'ids_dataframe'
fp_7 = 'column_dataframe.csv'

# # EXPORTING DATAFRAMES (WEIGHTS_PER_HOUSE, IDS, LENGTHS, WIDTH, DEPTH) TO CSV
# grid_chosen_house_dict['weight_per_house'].to_csv(fp_main + fp_2, index=None) 

# EXPORTING DATAFRAME FOR COLUMN DIMENSIONS AND TOLERANCE TO CSV
dfr_column =pd.DataFrame({'x_dim':[column_size], 'y_dim':[column_size], 'tolerance':[my_tolerance]})
dfr_column.to_csv(fp_main + fp_7, index=None) 





##############################################################################################################################

# specifying warehouses
warehouses = ["Warehouse_1", "Warehouse_2", "Warehouse_3", "Warehouse_4", "Warehouse_5", "Warehouse_6", "Warehouse_7", "Warehouse_8"]

###############################     PRE-DATAFRAME   ############################
from s0_preDataframe import assign_coordinates_and_distance,display,warehouse_combinations

locations_warehouses = assign_coordinates_and_distance(lat_1,lon_1)
display(folder_path=folder_path_server,folder_path_user = folder_path_user, locations_warehouses=locations_warehouses,lat_1=lat_1,lon_1=lon_1)
combinations_wh = warehouse_combinations(warehouses=warehouses,locations_warehouses=locations_warehouses)

###############################     DATAFRAME TO DICTIONARY     ############################

from s2_Dataframe_to_dictionary import lengths_into_groups, dataframe_to_dictionary
from pickle_commands import dump_into_pickle, pickle_open

dict_list = dataframe_to_dictionary(dataframe=df,tolerance=my_tolerance)
dump_into_pickle(file_path=os.path.join(folder_path_user, 'dict_list.pkl'),object=dict_list)

###############################     CREATE AXIAL COMBINATIONS   ############################
from s3_axial_combinations import axial_combinations

axial_combinations_dictionary = {}
axial_combinations_dictionary['y']=axial_combinations(axis_length=y_axis_length,axis_tolerance=axis_tolerance,dictionary=dict_list,column_size=column_size)
axial_combinations_dictionary['x']=axial_combinations(axis_length=x_axis_length,axis_tolerance=axis_tolerance,dictionary=dict_list,column_size=column_size)
dump_into_pickle(file_path=os.path.join(folder_path_user, 'axial_combinations_dictionary.pkl'), object=axial_combinations_dictionary)


###############################     POSSIBLE GRID COMBINATIONS      ############################
from s4_Possible_grid_combinations import make_grid_combinations

list_comb = make_grid_combinations(axial_combinations_dictionary=axial_combinations_dictionary)
dump_into_pickle(file_path=os.path.join(folder_path_user, 'list_comb.pkl'), object= list_comb)

###############################     GRID ATRRIBUTES GENERATION      ############################
from s5_Grid_attributes_generation import find_amount_of_houses,find_grids_optimized_for_house

possible_grids = find_grids_optimized_for_house(dict_list=dict_list,list_comb=list_comb,minimum_nohouses=minimum_nohouses)  

dump_into_pickle(file_path=os.path.join(folder_path_user, 'possible_grids.pkl'), object= possible_grids)


###############################     TRIBUTARY LOADING AREA DISTRIBUTION      ############################
from s6_tributary_load_area import tributary_load_area
''' 
The grid_master dictionary key order is: 

1) grid_number: 'grid_0', 'grid_1','grid_2' etc

2) type of data: 

    a) 'beams' 
        List of beams in x or y. list.

#     b) 'tr_area' 
#         Tributary loading area on beams in x or y. Dataframe.

#     c) 'tra_qty_pos_req' 

#     d) 'tra_qty_req'
#         Required number of beams for 1 house for each area. Dictionary.

#     e) 'tra_id_avail' (added later in static analysis part)
#         All unrefined possible ids of beams in x or y. Dictionary.

#     f) 'tra_qty_avail' (added later in static analysis part)
#         All unrefined possible quantities of beams in x or y. Dictionary.

#     g) 'tra_id_avail_ref_xy'(added later in static analysis part)
#         All refined possible ids of beams in x and y both in one dictionary. Dictionary.

#     h) 'tra_qty_avail_ref_xy'(added later in static analysis part)
#         All refined possible quantites of beams in x and y both in one dictionary. Dictionary.

# `   i) 'tra_id_avail_ref' (added later in static analysis part) 
#         All refined possible ids of beams in x or y separately. Dictionary. 

#     j) 'tra_qty_avail_ref' (added later in static analysis part) 
#         All refined possible quantites of beams in x or y separately. Dictionary. 

#     k) 'tra_id_avail_ref_wtsorted'(added later in self weight part)
#         Lightest ids of beams in x or y. Dictionary.

#     l) 'tra_qty_avail_ref_wtsorted' (added later in self weight part)
#         Lightest quantities of beams in x or y. Dictionary.

#     m) 'weight' (added later in self weight part)
#         Weight of the grid. 1 key gives total weight for all houses. 1 key gives weight per house. Dictionary.

#     n) 'missing_beams' (added later in self weight part)
#         Quantity of beams for each tributary area that are not satisfied by the stock. . Dictionary.

#     o) 'tra_qty_req_h' (added later in self weight part)
#         Required number of beams for a given number (h) of houses for each area. Dictionary.
     

# 3) x or y axis: this is true for all except g,h, and m

# '''
grid_master = tributary_load_area(possible_grids=possible_grids, dict_list=dict_list,column_size=column_size)
dump_into_pickle(file_path=os.path.join(folder_path_user,'grid_master.pkl'), object=grid_master)

###############################     STATIC ANALYSIS     ############################

from s8_static_analysis import static_analysis,refining_the_selection

grid_master_1= static_analysis(grid_master=grid_master,dict_list=dict_list,p_conc=p_conc,d_conc=d_conc)
dump_into_pickle(file_path=os.path.join(folder_path_user, 'grid_master_1.pkl'), object= grid_master_1)
grid_master_2 = refining_the_selection(grid_master=grid_master_1)
dump_into_pickle(file_path=os.path.join(folder_path_user, 'grid_master_2.pkl'), object= grid_master_2)


############################################    PICKLE  #######################################################

# # Specify the file path where you saved the dictionary
# file_path=os.path.join(folder_path_user, 'grid_master_2.pkl')
# # Load the dictionary from the file using Pickle
# with open(file_path, 'rb') as file:
#     grid_master_2 = pickle.load(file)



###############################     CHECK COLUMN SELFWEIGHT AND REMOVE MISSING BEAMS        ############################

from s9_check_column_slfwt_remove_miss_beams import removing_null_dictionaries,find_number_of_columns,solver_for_selfweight,filtering_for_required_no_houses

grid_master_3 = removing_null_dictionaries(grid_p_master=grid_master_2)
grid_master_4 = find_number_of_columns(grid_p_master=grid_master_3)
grid_master_5 = solver_for_selfweight(dict_list=dict_list,grid_p_master=grid_master_4, h = minimum_nohouses)
grid_master_6 = filtering_for_required_no_houses(grid_p_master=grid_master_5)

if (len(list(grid_master_6.keys()))) == 0:
    print('If you would like to choose a lesser number of houses, please rerun the simulation')
    print('---')
else:
    print("Let's try to find the best combination from our stock for you")
    print('---')
    print("Whilst we calulate your results, have a break, have a Kitkat")
    # time.sleep(1)
    print("(This tool is not sponsored)")
    print('---')
    dump_into_pickle(file_path=os.path.join(folder_path_user,'grid_master_6.pkl'), object=grid_master_6)

    #############################################    PICKLE  #######################################################

    # # Specify the file path where you saved the dictionary
    # file_path=os.path.join(folder_path_user, 'grid_master_6.pkl')
    # # Load the dictionary from the file using Pickle
    # with open(file_path, 'rb') as file:
    #     grid_master_6 = pickle.load(file)
    # print(f"first 10 keys of grid_master_6 are{list(grid_master_6.keys())[:10]} out of {len(list(grid_master_6.keys())[:10])}) grids")

    ################################# DISTANCE FROM WAREHOUSE #############################################

    from s10_distance_from_warehouse_2 import distance_from_warehouse, grids_with_keys_as_objectives

    grid_master_7 = distance_from_warehouse(grid_p_master_2 = grid_master_6, locations_warehouses = locations_warehouses, combinations_wh = combinations_wh, dict_list = dict_list, h = minimum_nohouses, weight_per_truck = weight_per_truck)

    # pp.pprint(grid_master_7['grid_167']['distance']['dist_total'])
    # print('----')
    # print('----')
    # pp.pprint(grid_master_7['grid_1421']['distance']['dist_total'])
    # print('----')
    # print('----')
    # pp.pprint(grid_master_7['grid_167']['weight']['dist_total'])


    data = grids_with_keys_as_objectives(grid_master_to_test = grid_master_7)

    dump_into_pickle(file_path=os.path.join(folder_path_user,'grid_master_7.pkl'), object=grid_master_7)
    dump_into_pickle(file_path=os.path.join(folder_path_user,'data.pkl'), object=data)

    #############################################    PICKLE  #######################################################

    # # Specify the file path where you saved the dictionary
    # file_path=os.path.join(folder_path_user, 'grid_master_7.pkl')
    # # Load the dictionary from the file using Pickle
    # with open(file_path, 'rb') as file:
    #     grid_master_7 = pickle.load(file)

    # # Specify the file path where you saved the dictionary
    # file_path=os.path.join(folder_path_user, 'data.pkl')
    # # Load the dictionary from the file using Pickle
    # with open(file_path, 'rb') as file:
    #     data = pickle.load(file)
        
    # # print(f"first 10 keys of grid_master_7 are{list(grid_master_7.keys())[:10]} out of {len(list(grid_master_7.keys()))}) grids")
    ##################################################   OPTIMIZATION  ################################################

    from s13_Optimization import optimization, plot_points
    optimized_data, best_obj2_and_closest_to_obj1, best_obj1_and_closest_to_obj2, second_best_obj = optimization(Obj_1=Obj_1,Obj_2=Obj_2,data=data)
    plot_points(data,optimized_data,best_obj2_and_closest_to_obj1,best_obj1_and_closest_to_obj2,second_best_obj, Obj_1, Obj_2)



    print(f"The best grids for {Obj_2} are")
    print((list(best_obj2_and_closest_to_obj1.keys()))[0])
    # include the which warehouse the grid belongs to
    print('---')

    print(f"The best grids for {Obj_1} are")
    print((list(best_obj1_and_closest_to_obj2.keys()))[0])
    # include the which warehouse the grid belongs to
    print('---')
    
    second_best_obj_result = len(list(second_best_obj.keys()))
    if second_best_obj_result != 0:
        print("The second best grids are")
        print((list(second_best_obj.keys()))[0])
        # include the which warehouse the grid belongs to
        print('---')

    ############################   HOUSE PROPERTIES FOR CHOSEN GRID   ###################################################

    from s12_beam_distribution_for_best_grid import beam_distribution_for_best_grid, print_csv_dict_nested_1stlevel, print_csv_dataframe_per_house

    # choose the grid
    user_input = input('Place chosen grid number here: (e.g to choose grid_1234, type "1234")')
    chosen_grid = f"grid_{user_input}"
    grid_chosen = grid_master_7[chosen_grid]
    print('---')
    print(f"chosen warehouse is {chosen_grid}")
    print('---')

    # choose the warehouse combination
    user_input = input('Place chosen warehouse combination here: (e.g to choose combination [Warehouse_1, Warehouse_2,Warehouse_3], type "1,2,3" in the correct order)')
    warehouses_chosen = [f"Warehouse_{i}" for i in user_input if i != ',']
    print('---')
    print(f"chosen warehouse is {warehouses_chosen}")
    print('---')

    house_index = [f"house_{i}" for i in range(1,minimum_nohouses+1)]

    # print('house properties for chosen grid starts here')

    grid_chosen_house_dict = beam_distribution_for_best_grid(grid = grid_chosen, h = minimum_nohouses, wh=warehouses_chosen, house_index= house_index, df= df)
    dump_into_pickle(file_path=os.path.join(folder_path_user,'grid_chosen_house_dict.pkl'), object=grid_chosen_house_dict)



    ##############################################      TESTING MAIN DATA  ###############################################

    # print(f"first 10 keys of grid_master_7 are{list(grid_master_7.keys())[:7]} out of {len(list(grid_master_7.keys())[:10])}) grids")
                    

    # print('---PRINTING CODE: PLACE NO COLUMNS AND SELFWEIGHT STARTS HERE---')

    # grid_p_master = grid_master_7
    # grid_to_test=(list(grid_p_master.keys())[0])
    # b_type = 'B7'
    # print(grid_to_test)

    # print('---HERE---')
    # pp.pprint(data.keys())
    # print(grid_master_6.keys())
    # print('---HERE---')
    # print(f"number of houses are {grid_p_master[grid_to_test]['number_of_houses']}")
    # print('---HERE---')
    # print(f"refined avail_qty in x are {grid_p_master[grid_to_test]['tra_qty_avail_ref']['x'][b_type]}")
    # print('---HERE---')
    # print(f"unrefined avail_qty in x are {grid_p_master[grid_to_test]['tra_qty_avail']['x'][b_type]}")
    # print('---HERE---')
    # print(f"missing_beams is {grid_p_master[grid_to_test]['missing_beams']}")
    # # print('---HERE---')
    # # print(f"weight is {grid_p_master[grid_to_test]['weight']}")
    # print('---HERE---')
    # print(f"Column quantity is {grid_p_master[grid_to_test]['column_qty']}")
    # print('---HERE---')
    # print(f"req_qty for 1 house are {grid_p_master[grid_to_test]['tra_qty_req']['x'][b_type]}")
    # # print('---HERE---')
    # # print(f"used_id_sorted are {grid_p_master[grid_to_test]['tra_id_used_ref_wtsorted']}")
    # print('---HERE---')
    # print(f"required_qty for {minimum_nohouses} houses are {grid_p_master[grid_to_test]['tra_qty_req_h']['x'][b_type]}")
    # # print('---HERE---')
    # # print(f"used_qty_sorted are {grid_p_master[grid_to_test]['tra_qty_used_ref_wtsorted']}")
    # print('---HERE---')
    # print(f"tributary loading area are")
    # print(grid_p_master[grid_to_test]['tr_area']['x'])
    # print('---HERE---')
    # print(f"keys are {list(grid_p_master[grid_to_test].keys())}")
    # print('---HERE---')
    # print(f"master grid with missing beam grids has {len(list(grid_p_master.keys()))} keys")
    # print('---HERE---')
    # print(f"master grid without missing beam grids has {len(list(grid_master_5.keys()))} keys")
    # print(dict_list.keys())


    ##################################  CONFIRM STOCK ORDER  #################################

    user_input = input('Would you like to buy the stock? (Yes/No)')
    answer = str(user_input)

    if answer == 'yes' or answer == 'Yes' or answer == 'YES':
        print('---')
        print('Booking has been made')

        #################################################   EXPORTING  ###################################################

        '''
        # The following keys have not been exported to folder:

        1) beams
        2) distance

        '''
        # print('---')
        # user_input = input('Place file-path to download excel sheets of your houses: (eg "D:/OneDrive - Delft University of Technology/CORE/python files/final_csv_set')
        # fp_main  = str(user_input)

        # Specify the file paths for CSV set

        fp_main=os.path.join(folder_path_user,'csv_set/')
        if not os.path.exists(fp_main):
            os.makedirs(fp_main)
        
        fp_1 = 'ids_per_warehouse.csv'
        fp_2 = 'weight_per_house.csv'
        fp_3 = 'depths_dataframe'
        fp_4 = 'lengths_dataframe'
        fp_5 = 'widths_dataframe'
        fp_6 = 'ids_dataframe'
        fp_7 = 'column_dataframe'

        # EXPORTING DATAFRAMES (WEIGHTS_PER_HOUSE, IDS, LENGTHS, WIDTH, DEPTH) TO CSV
        grid_chosen_house_dict['weight_per_house'].to_csv(fp_main + fp_2, index=None) 

        # EXPORTING DATAFRAME FOR COLUMN DIMENSIONS AND TOLERANCE TO CSV
        dfr_column =pd.DataFrame({'x_dim':[column_size], 'y_dim':[column_size], 'tolerance':[my_tolerance]})
        dfr_column.to_csv(fp_main + fp_7, index=None) 

        # ids_per_warehouse
        print_csv_dict_nested_1stlevel(grid_chosen_house_dict['ids_per_warehouse'],'House', 'Warehouse', 'ID', fp_main+fp_1)

        # depths_dataframe, lengths_dataframe, widths_dataframe, ids_dataframe
        print_csv_dataframe_per_house(grid_houses = grid_chosen_house_dict, house_index = house_index,fp_main = fp_main, fp_3 = fp_3, fp_4 = fp_4, fp_5=fp_5, fp_6=fp_6)

        print('---')
        print('Stock has been reserved for you')
        print('---')
        print('Excel sheets of the reserved stock have been uploaded to your folder')
        print('---')
        print('The transportation map from our warehouses to your site has been uploaded to your folder')

        ################################################   DELETE BEAMS  ################################################
        from s14_Delete_beams import * 

        delete_beams_from_df(df = df, best_grid = grid_chosen)
        print('---')
        print('We have updated our inventory so your reserved stock has been removed from it')




# Record the end time
end_time = time.time()
# Calculate the execution time
execution_time = end_time - start_time


print('---')
print(f"Execution time using time module: {round(execution_time*1000,3)} milliseconds")
print('---')
print('-------------------------------------------THANK YOU FOR USING RE_CONC_STRUCT-------------------------------------------')
