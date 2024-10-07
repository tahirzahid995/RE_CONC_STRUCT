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
from s2_Dataframe_to_dictionary import new_dict_list
import plotly.graph_objects as go
# from s6_tributary_load_area import tributary_areas_x
# from s2_Dataframe_to_dictionary import dict_list
# from s0_preDataframe import warehouses
# from s9_Place_no_columns_and_selfweight_version1 import h

pp = pprint.PrettyPrinter()


# Specify the file path where you saved the dictionary
file_path = "D:\OneDrive - Delft University of Technology\CORE\python files\Script_28_10_2023\grid_master_3.pkl"
# Load the dictionary from the file using Pickle
with open(file_path, 'rb') as file:
    grid_p_master_3 = pickle.load(file)


# Specify the file path where you saved the dictionary
file_path = "D:\OneDrive - Delft University of Technology\CORE\python files\Script_28_10_2023\dict_optimized_wh_comb.pkl"
# Load the dictionary from the file using Pickle
with open(file_path, 'rb') as file:
    dict_p_optimized_wh_comb = pickle.load(file)


# Specify the file path where you saved the dictionary
file_path = "D:\OneDrive - Delft University of Technology\CORE\python files\Script_28_10_2023\dict_objective_wh_comb.pkl"
# Load the dictionary from the file using Pickle
with open(file_path, 'rb') as file:
    dict_p_objective_wh_comb = pickle.load(file)


# filter 
print((list(dict_p_objective_wh_comb.keys()))) 
dict_p_objective_wh_comb = filter_dictionary(dict_p_objective_wh_comb,20) 
# dict_p_objective_wh_comb = dict_p_objective_wh_comb['grid_6803']

# print(dict_p_objective_wh_comb.keys())
# pp.pprint(dict_p_objective_wh_comb)
data = dict_p_objective_wh_comb
# dict_p_optimized_wh_comb = filter_dictionary(dict_p_optimized_wh_comb,5) 
# print(dict_p_optimized_wh_comb.keys())
# pp.pprint(dict_p_optimized_wh_comb)
print(data) 

dict_list = new_dict_list

def optimize_with_warehouses(data):
    # Initialize lists to store distance, weight, and grid combinations
    all_distances = []
    all_weights = []
    combinations = []

    # Extract all distance and weight values from the data and create combinations
    for grid_name, grid_data in data.items():
        for combination, values in grid_data.items():
            all_distances.append(values['distance'])
            all_weights.append(values['weight'])
            combinations.append(f"{grid_name} - {combination}")

    # Find the minimum distance and minimum weight values
    min_distance = min(all_distances)
    min_weight = min(all_weights)

    # Create a list of colors with a special color for the points with both minimum distance and minimum weight
    colors = ['blue' if dist != min_distance or weight != min_weight else 'red' for dist, weight in zip(all_distances, all_weights)]

    # Create a scatter plot with hover labels
    fig = go.Figure()

    # Add traces for all warehouse combinations for each grid with colors
    for i, combination in enumerate(combinations):
        fig.add_trace(go.Scatter(
            x=[all_distances[i]],
            y=[all_weights[i]],
            mode='markers+text',
            text=[combination],
            textposition='bottom center',
            marker=dict(size=10, color=colors[i]),
        ))

    # Set axis labels and title
    fig.update_layout(
        xaxis_title='Distance',
        yaxis_title='Weight',
        title='Scatter Plot of Distance vs Weight for Warehouse Combinations in Multiple Grids',
    )

    # Decrease the font size of hover labels
    fig.update_traces(textfont=dict(size=1))  # Adjust the font size here

    # Show the plot
    fig.show()
    # return fig

optimize_with_warehouses(data)
