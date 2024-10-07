import matplotlib.pyplot as plt
import time
import json
import numpy as np
import matplotlib.pyplot as plt
import pprint 
import plotly.graph_objects as go
# # Load data from the JSON file
# with open("possible_grids.json", 'r') as file:
#     possible_grids = json.load(file)
# from pickle_commands import pickle_open
# file_path = 'C:\\Codes\\Core\\OneDrive_1_28-10-2023\\revised_code\\possible_grids.pkl'
# # possible_grids = pickle_open(file_path=file_path)
# data = pickle_open(file_path=r"C:\Codes\Core\OneDrive_1_28-10-2023\revised_code\data.pkl")



################################OPTIMIZATION#######################

def optimization(Obj_1,Obj_2,data):
    # Initialize dictionaries to store data for different categories
    optimized_data = {}  # Blue
    best_obj1_solutions = {}  # Red
    best_obj2_solutions = {}  # Yellow
    best_obj1_and_closest_to_obj2 = {}  # Green
    best_obj2_and_closest_to_obj1 = {}  # Purple
    second_best_obj = {}  # Orange
    # second_best_obj2 = {}  # Pink

    # # Find the grid(s) that maximize 'Objective 1'
    # max_obj1_value = float('-inf')
    # for grid_name, point in possible_grids.items():
    #     obj1_value = point[Obj_1]
    #     if obj1_value > max_obj1_value:
    #         max_obj1_value = obj1_value
    #         best_obj1_solutions = {grid_name: point}
    #     elif obj1_value == max_obj1_value:
    #         best_obj1_solutions[grid_name] = point


    # Find the grid(s) that minimize 'Objective 1'
    max_obj1_value = float('inf')
    for grid_name, info in data.items():
        for point in info.values():
            obj1_value = point[Obj_1]
            if obj1_value < max_obj1_value:
                max_obj1_value = obj1_value
                best_obj1_solutions = {grid_name: point}
            elif obj1_value == max_obj1_value:
                best_obj1_solutions[grid_name] = point

    # Find the grid(s that minimize 'Objective 2'
    min_obj2_value = float('inf')
    for grid_name, info in data.items():
        for point in info.values():
            obj2_value = point[Obj_2]
            if obj2_value < min_obj2_value:
                min_obj2_value = obj2_value
                best_obj2_solutions = {grid_name: point}
            elif obj2_value == min_obj2_value:
                best_obj2_solutions[grid_name] = point

    #Filter the best solutions for Objective 1 to find the one closest to Objective 2

    best_obj1_and_closest_to_obj2 = {}
    min_distance_to_obj2 = float('inf')

    for grid_name, point in best_obj1_solutions.items():
        distance_to_obj2 = abs(point[Obj_2] - min_obj2_value)

        if distance_to_obj2 < min_distance_to_obj2:
            best_obj1_and_closest_to_obj2 = {grid_name: point}
            min_distance_to_obj2 = distance_to_obj2
        elif distance_to_obj2 == min_distance_to_obj2:
            best_obj1_and_closest_to_obj2[grid_name] = point


    #Filter the best solutions for Objective 2 to find the one closest to Objective 1
    best_obj2_and_closest_to_obj1 = {}
    min_distance_to_obj1 = float('inf')

    for grid_name, point in best_obj2_solutions.items():
        distance_to_obj1 = abs(point[Obj_1] - max_obj1_value)

        if distance_to_obj1 < min_distance_to_obj1:
            best_obj2_and_closest_to_obj1 = {grid_name: point}
            min_distance_to_obj1 = distance_to_obj1
        elif distance_to_obj1 == min_distance_to_obj1:
            best_obj2_and_closest_to_obj1[grid_name] = point

            
    # Find solutions that are better than the best solution for Objective 2 but not as good as the best for Objective 1
    second_best_obj = {}
    grid_obj1 = list(best_obj1_and_closest_to_obj2.values())[0]
    grid_obj2 = list(best_obj2_and_closest_to_obj1.values())[0]
            
    for grid_name in data:
        for wh_combi, point in data[grid_name].items():
            if point[Obj_1] < grid_obj2[Obj_1] and point[Obj_2]<grid_obj1[Obj_2]:
                if grid_name in second_best_obj:
                    second_best_obj[grid_name][wh_combi] = point
                else: 
                    second_best_obj[grid_name]={}
                    second_best_obj[grid_name][wh_combi] = {}
                    second_best_obj[grid_name][wh_combi] = point
    
    '''    # pareto_front = {}

        # # Create a Pareto front for each grid
        # for grid_name, warehouses in second_best_obj.items():
        #     pareto_front[grid_name] = {}
            
        #     # Convert the warehouse data into a list of points
        #     points = list(warehouses.values())
            
        #     for i, point in enumerate(points):
        #         is_pareto = True
                
        #         for other_point in points:
        #             if (
        #                 point[Obj_1] > other_point[Obj_1] and
        #                 point[Obj_2] > other_point[Obj_2]
        #             ):
        #                 is_pareto = False
        #                 break

        #         if is_pareto:
        #             pareto_front[grid_name][i] = point

        # # Convert the Pareto front back to dictionaries
        # for grid_name, pareto_points in pareto_front.items():
        #     second_best_obj[grid_name] = {f'warehouse_{i}': point for i, point in pareto_points.items()}
    '''

   
    #Filter values to not exist in all categories on the same time        
    # Remove grids from Second Objective1 if they exist in Best Obj 1 and closest to obj 2
    remove_grids = []
    for gridname, warehouses in second_best_obj.items(): 
        for warehouse_name, point in warehouses.items():#where point is warehouse data
                for grids,attributes in best_obj1_and_closest_to_obj2.items():
                    if (point[Obj_1] == attributes[Obj_1]) and (point[Obj_2] == attributes[Obj_2]): 
                        remove_grids.append(gridname)

    for grids in remove_grids:
        if grids in second_best_obj:
            del second_best_obj[grids]

    # Remove grids from Second Objective2 if they exist in Best Obj 2 and closest to obj 1
    remove_grids = []
    for gridname, warehouses in second_best_obj.items(): 
        for warehouse_name, point in warehouses.items():#where point is warehouse data
            if (point[Obj_1] == attributes[Obj_1]) and (point[Obj_2] == attributes[Obj_2]): 
                remove_grids.append(gridname)

    for grids in remove_grids:
        if grids in second_best_obj:
            del second_best_obj[grids]
    return optimized_data,best_obj2_and_closest_to_obj1,best_obj1_and_closest_to_obj2,second_best_obj

################################PLOT###################################

import pandas as pd
import plotly.express as px


def plot_points(data, optimized_data, best_obj2_and_closest_to_obj1, best_obj1_and_closest_to_obj2, second_best_obj, Obj_1, Obj_2, text_font_size=1, text_opacity=0.8):
    # Create a list to store all data points and labels
    points = []
    labels = []
    groups = []

    # Add original data points to the list
    for grid_name, info in data.items():
        for point_name, point_data in info.items():
            x = point_data[Obj_1]
            y = point_data[Obj_2]
            label = f"{grid_name} - {point_name}<br>{Obj_1}: {x}, {Obj_2}: {y}"
            points.append((x, y))
            labels.append(label)
            groups.append('Original Data')

    # Add best solutions to the list
    for grid_name, point_data in best_obj2_and_closest_to_obj1.items():
        x = point_data[Obj_1]
        y = point_data[Obj_2]
        label = f"{grid_name}<br>{Obj_1}: {x}, {Obj_2}: {y}"
        points.append((x, y))
        labels.append(label)
        groups.append('Best Objective 2')

    for grid_name, point_data in best_obj1_and_closest_to_obj2.items():
        x = point_data[Obj_1]
        y = point_data[Obj_2]
        label = f"{grid_name}<br>{Obj_1}: {x}, {Obj_2}: {y}"
        points.append((x, y))
        labels.append(label)
        groups.append('Best Objective 1')

    # Add second-best solutions to the list
    for grid_name, warehouses in second_best_obj.items():
        for warehouse_name, point_data in warehouses.items():
            x = point_data[Obj_1]
            y = point_data[Obj_2]
            label = f"{grid_name} - {warehouse_name}<br>{Obj_1}: {x}, {Obj_2}: {y}"
            points.append((x, y))
            labels.append(label)
            groups.append('Second Best Objective')

    # Create a DataFrame from the points, labels, and groups
    df = pd.DataFrame({'x': [point[0] for point in points], 'y': [point[1] for point in points], 'label': labels, 'group': groups})

    # Define custom colors for each group
    custom_colors = {'Original Data': 'pink', 'Best Objective 2': 'blue', 'Best Objective 1': 'green', 'Second Best Objective': 'orange'}

    # Create a scatter plot using Plotly Express
    fig = px.scatter(df, x='x', y='y', text='label', color='group', color_discrete_map=custom_colors, labels={'x': Obj_1, 'y': Obj_2})

    # Set the title
    fig.update_layout(title='Grid Solutions')

    # Update the text font size and opacity
    fig.update_traces(textfont=dict(size=text_font_size), selector=dict(mode='markers+text'))
    fig.update_traces(marker=dict(opacity=text_opacity))

    # Show the plot
    fig.show()





