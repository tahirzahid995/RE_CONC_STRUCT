#Delete beams

import json
import pickle
import pandas as pd

#from s5_COMPARE_QUANTITY_OF_BEAMS_IN_YOUR_DICTI import minimum_nohouses
#from Simple_optimization import best_grid
#from Pareto_dominance_analysis import pareto_front
#from s7_static_analysis import grid_master

# Specify the file path where you saved the dictionary
# file_path = r"D:/OneDrive - Delft University of Technology/CORE/python files/revised_code/grid_master_6.pkl"
# df_path = r"C:\Codes\Core\OneDrive_1_28-10-2023\revised_code\Dataframe2.csv"

# minimum_nohouses = 50
# Load the dictionary from the file using Pickle
# with open(file_path, 'rb') as file:
#     grid_master = pickle.load(file)

# Read the DataFrame from your source, for example, a CSV file
# df = pd.read_csv("C:\Codes\Core\OneDrive_1_20-10-2023/Dataframe2.csv")

# best_grid = best_grid1['grid_4458']

# available_beam_ids = best_grid['tra_id_avail_ref_wtsorted']

# print(available_beam_ids)
# for each_id in best_grid['']
# print(available_beam_ids)
# ID value to delete

# id_to_delete = '12345'



def delete_beams_from_df(df, best_grid):
    # print('Which grid do you choose?')
    
    for warehouse in best_grid['tra_id_used_ref_wtsorted']: 
        for axis in best_grid['tra_id_used_ref_wtsorted'][warehouse]: 
            for beam_type in best_grid['tra_id_used_ref_wtsorted'][warehouse][axis]:
                for area in best_grid['tra_id_used_ref_wtsorted'][warehouse][axis][beam_type]:
                    for i in best_grid['tra_id_used_ref_wtsorted'][warehouse][axis][beam_type][area]:
                        id_to_delete = i
                        
                        # Find the index of the row with the specified ID
                        index_to_delete = df[df['IDs'] == id_to_delete].index

                        # Check if the ID exists in the DataFrame
                        if not index_to_delete.empty:
                            # Delete the row with the specified ID
                            df = df.drop(index_to_delete)

                            # Reset the index to maintain continuity (optional)
                            df = df.reset_index(drop=True)

                            # print(f"Row with ID {id_to_delete} deleted.")
                        else:
                            pass
                            # print(f"ID {id_to_delete} not found in the DataFrame.")

        # print('The beams are now deleted from the directory')
# Now, df does not contain the row with the specified ID.



 



