import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import copy
import time
import pickle


from s7_refinement_functions import remove_repetitions_across_keys
from s7_refinement_functions import merge_double_nested_dicts





# '''
# # DEAD LOAD 
# dead_load in N/m^2 = d_load_psqm
# length of beam in m = l
# area = tributray loading area on beam

# # Concrete
# density in kg/m^3= p_conc
# thickness of slab m^2 = d_conc

# '''
# p_conc = 2400
# d_conc = 0.2
# sample area = 4       to be linked to grid
# sample beam_length = 4    to be linked to grid


# d_load_psqm = int(p_conc*d_conc*9.81*1.35)


'''
# dead load per sq.m * area = dead load in N 
# Moment max at midspan for simply supported beam under UDL = Wl/8 where l W is dead load in N
# Shear load max at supports for simply supported beam under UDL = wl/2 
'''


'''
# df_sample = df.head(10)
# print(df_sample)



# # Cutting the main dataframe into smaller dataframes. The keys are beam types (B1,B2 etc) and the values are the dataframes
# df_dict={}
# length_list = {'B1':1,'B2':2,'B3':3,'B4':4,'B5':5,'B6':6,'B7':7,'B8':8,'B9':9}

# for i, key in enumerate(length_list.keys()):
#     val = length_list[key]
#     df_dict[key]={}
#     condition = (df['lengths'] > val -0.9) & (df['lengths'] <= val)
#     df_dict[key]=df[condition]

# # df_qty is the quantity of stock beams in each beam type (B1, B2  etc)
# df_qty = {}
# for key, dataframe in df_dict.items():
#     df_qty[key] = dataframe.shape[0]
# # n_total is the total quantity of stock beams in each beam type
# n_total = 0
# for key, n in df_qty.items():
#     n_total+= n
'''



#################################################   STATIC ANALYSIS SOLVER    ###########################################
def static_analysis(grid_master,dict_list,p_conc,d_conc):
    
    d_load_psqm = int(p_conc*d_conc*9.81*1.35)
    
    # Label for keys in the dictionary
    labels = ['x','y']


    rejected_beams = 0
    for grid in grid_master.keys():
        
        # making a dictionary in each grid for available quantity of beams that are required
        grid_master[grid]['tra_id_avail'] = {} 
        grid_master[grid]['tra_qty_avail'] = {} 

        # making a dictionary for the x or y axis
        for l in labels:
            grid_master[grid]['tra_id_avail'][l]={}
            grid_master[grid]['tra_qty_avail'][l]={}

            for beam_type in grid_master[grid]['tra_qty_req'][l].keys():
                beam_length = dict_list[beam_type]['LENGTH']
                grid_master[grid]['tra_id_avail'][l][beam_type]={}
                grid_master[grid]['tra_qty_avail'][l][beam_type]={}
                

                for i, area in enumerate(grid_master[grid]['tra_qty_req'][l][beam_type].keys()):
                    
                    qty = 0
                    
                    # making empty dictionaries
                    grid_master[grid]['tra_id_avail'][l][beam_type][area]={}
                    grid_master[grid]['tra_qty_avail'][l][beam_type][area]={}

                    # moment calculation
                    moment_applied = ((d_load_psqm*area)*beam_length)/8

                    # shear calculation
                    shear_load = (d_load_psqm*area)/2

                    # checking if applied moment < Mu of conc and applied moment < Mu of steel
                    condition_1 = (dict_list[beam_type]['DATAFRAME']['ultimate_bending_moment_concrete'] > moment_applied) & (dict_list[beam_type]['DATAFRAME']['ultimate_bending_moment_steel'] > moment_applied)
                
                    # ADD shear check HERE!!!!!!!!!!!!!!!!!!!



                    if any(condition_1):

                        # id is the beam identity
                        id = list(dict_list[beam_type]['DATAFRAME'][condition_1]['IDs'])
                        # qty is the number of beams that satsify the tributary loading area
                        qty = len(list(dict_list[beam_type]['DATAFRAME'][condition_1]['IDs']))

                        # adding the id to grid_master
                        grid_master[grid]['tra_id_avail'][l][beam_type][area]= id
                        
                    
                    elif not any(condition_1):
                        rejected_beams +=1
                    
                    # adding the qty to grid_master
                    grid_master[grid]['tra_qty_avail'][l][beam_type][area]= qty  

    return grid_master

'''# print(grid_master['grid_1']['tra_id_avail']['x'])
# print("---")
# print(grid_master['grid_1']['tra_qty_req']['x'])
# print("---")
# print(grid_master['grid_1']['tra_qty_avail']['x']['B4'])


#print(rejected_beams)
'''


###############################################    REFINING THE SELECTION  #########################################
def refining_the_selection(grid_master):
    for grid in grid_master.keys():

        # merging x and y of tra_id_avail
        grid_xy = merge_double_nested_dicts(grid_master[grid]['tra_id_avail'])

        # for x,y combined
        grid_master[grid]['tra_qty_avail_ref_xy']={}
        grid_master[grid]['tra_id_avail_ref_xy']={}
        # for x,y separate
        grid_master[grid]['tra_id_avail_ref'] ={}
        grid_master[grid]['tra_id_avail_ref']['x'] ={}
        grid_master[grid]['tra_id_avail_ref']['y'] ={}
        grid_master[grid]['tra_qty_avail_ref']={}
        grid_master[grid]['tra_qty_avail_ref']['x']={}
        grid_master[grid]['tra_qty_avail_ref']['y']={}
        
        for beam_type in grid_xy:
            y = remove_repetitions_across_keys(grid_xy[beam_type])
            
            # for x,y combined
            grid_master[grid]['tra_qty_avail_ref_xy'][beam_type]={}
            grid_master[grid]['tra_id_avail_ref_xy'][beam_type] ={}
            grid_master[grid]['tra_id_avail_ref_xy'][beam_type] = y
            
            
        
            # for x,y separate
            grid_master[grid]['tra_id_avail_ref']['x'][beam_type]={}
            grid_master[grid]['tra_id_avail_ref']['y'][beam_type]={}
            grid_master[grid]['tra_qty_avail_ref']['x'][beam_type]={}
            grid_master[grid]['tra_qty_avail_ref']['y'][beam_type]={}

            
            for area, ids in y.items():
                qty = len(ids)
                
                # for x,y combined
                grid_master[grid]['tra_qty_avail_ref_xy'][beam_type][area] ={}
                grid_master[grid]['tra_qty_avail_ref_xy'][beam_type][area] = qty
            
                # for x,y separate
                if area[-1] == 'x':
                    grid_master[grid]['tra_id_avail_ref']['x'][beam_type][float(area[:-1])]={}
                    grid_master[grid]['tra_qty_avail_ref']['x'][beam_type][float(area[:-1])]={}
                    grid_master[grid]['tra_id_avail_ref']['x'][beam_type][float(area[:-1])] = ids
                    grid_master[grid]['tra_qty_avail_ref']['x'][beam_type][float(area[:-1])] = qty
                else:
                    grid_master[grid]['tra_id_avail_ref']['y'][beam_type][float(area[:-1])]={}
                    grid_master[grid]['tra_qty_avail_ref']['y'][beam_type][float(area[:-1])]={}
                    grid_master[grid]['tra_id_avail_ref']['y'][beam_type][float(area[:-1])] = ids
                    grid_master[grid]['tra_qty_avail_ref']['y'][beam_type][float(area[:-1])] = qty
    return grid_master

################################################   TESTING REFINEMENT  #########################################

''''print('---PRINTING CODE: STATIC ANALYSIS STARTS HERE---')




# Specify the file path where you want to save the dictionary
file_path = "D:\OneDrive - Delft University of Technology\CORE\python files\Script_28_10_2023\grid_master.pkl"

# Save the dictionary to a file using Pickle
with open(file_path, 'wb') as file:
    pickle.dump(grid_master, file)




grid_to_test=((list(grid_master.keys())[8]))
b_type = 'B3'
print(grid_to_test)
# print(f"beams are {grid_master[grid_to_test]['beams']}")
# print('---HERE---')
# print(f"x has available {grid_master[grid_to_test]['tra_id_avail_ref']['x']}")
# print('---HERE---')
# print(f"x has required {grid_master[grid_to_test]['tra_qty_req']['x']}")
# print('---HERE---')
# print(f"x has available required {grid_master[grid_to_test]['tra_qty_avail_ref']['x']}")
# print('---HERE---')
# print(f"COMBINED has {grid_master[grid_to_test]['tra_qty_avail_ref_xy']}")

# print('---HERE---')
# print(f"COMBINED has {sum(grid_master[grid_to_test]['tra_qty_avail_ref_xy'][b_type].values())} BEAMS")
# print(f"INDIVDUAL SUM has {sum(grid_master[grid_to_test]['tra_qty_avail_ref']['x'][b_type].values())+sum(grid_master[grid_to_test]['tra_qty_avail_ref']['y'][b_type].values())} BEAMS")
# print(f"UNREFINED has {grid_master[grid_to_test]['tra_qty_avail']['x'][b_type]}")






# Record the end time
end_time = time.time()
# Calculate the execution time
execution_time = end_time - start_time
print(f"Execution time using time module: {round(execution_time*1000,3)} milliseconds")'''

