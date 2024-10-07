import pandas as pd
import numpy as np
import json
import time
import pickle
import copy
import matplotlib.pyplot as plt
import folium
import math
import itertools
import pprint 
import os
from datetime import datetime
#from s2_Dataframe_to_dictionary import dict_list

from s7_refinement_functions import *
pp = pprint.PrettyPrinter()

from pickle_commands import pickle_open

#specifying warehouses
warehouses = ["Warehouse_1", "Warehouse_2", "Warehouse_3", "Warehouse_4", "Warehouse_5", "Warehouse_6", "Warehouse_7", "Warehouse_8"]


######################################################## DICTIONARY FOR WAREHOUSES ###########################################


# # Input latitude and longitude coordinates from the user in a single prompt
# location_home = input("Enter latitude and longitude (comma-separated): ")
# # coordinates of home
# lat_1, lon_1 = map(float, location_home.split(','))

# sample coordinates
lat_1 = 37.5419
lon_1 = 36.8324

######################################################## ASSIGN COORDINATES AND DISTANCE ###########################################
def assign_coordinates_and_distance(lat_1,lon_1):
    wh_coords = [[37.455, 37.7232], [37.3564, 36.6886],[37.6632, 38.1566],[37.3769, 37.3576], [37.062, 37.0322],[37.7208, 37.0404],[37.8338, 36.4032],[37.4562, 36.3415]]

    locations_warehouses = {}
    for name, wh_coord in zip (warehouses, wh_coords):
        lat_2 = wh_coord[0]
        lon_2 = wh_coord[1]
        distance = haversine_distance(lat_1,lon_1,lat_2,lon_2)
        locations_warehouses[name]= {}
        locations_warehouses[name]['coordinates'] = wh_coord
        locations_warehouses[name]['distance'] = distance
    return locations_warehouses

# print(locations_warehouses)


######################################################## DISPLAY ###########################################
def display(folder_path, folder_path_user, locations_warehouses, lat_1, lon_1):
    # Create a map centered at a specific location (e.g., latitude and longitude)
    map_center = (lat_1, lon_1)  # Kahramanmaras, Turkey

    # Create a folium map
    m = folium.Map(location=map_center, zoom_start=9)

    # Create the 'maps' folder if it doesn't exist
    maps_folder = os.path.join(folder_path_user,'maps')
    os.makedirs(maps_folder, exist_ok=True)

    icon_images = {}
    for key in locations_warehouses.keys():
        icon_images[key] = os.path.join(folder_path, 'warehouse_location_markers', key + '.png')

    # Generate a unique name for each map file using a timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    map_filename = f'locations_map_{timestamp}.html'

    # Add custom markers with labels for the warehouse locations
    for key in locations_warehouses.keys():
        lat = locations_warehouses[key]['coordinates'][0]
        lon = locations_warehouses[key]['coordinates'][1]
        custom_icon = folium.CustomIcon(
            icon_image=icon_images[key],
            icon_size=(40, 40),
        )
        folium.Marker(
            location=(lat, lon),
            icon=custom_icon,
            tooltip=key
        ).add_to(m)

    # Add custom marker with label for the home location
    custom_icon = folium.CustomIcon(
        icon_image=os.path.join(folder_path, 'warehouse_location_markers', 'home.png'),
        icon_size=(40, 40)
    )
    folium.Marker(
        location=(lat_1, lon_1),
        icon=custom_icon,
        tooltip='home'
    ).add_to(m)

    # Save the map with the unique filename
    map_path = os.path.join(maps_folder, map_filename)
    m.save(map_path)



######################################################## WAREHOUSE COMBINATIONS ###########################################
def warehouse_combinations(warehouses,locations_warehouses):
    def first_warehouse_combinations(warehouses):
        combinations_wh = []
        for i in range(1, (len(warehouses)+1)):
            for combinations in itertools.combinations(warehouses,i):
                combinations_wh.append(combinations)
        # convert the tuples inside the list into lists
        combinations_wh = [list(i) for i in combinations_wh]
        return combinations_wh
    # pp.pprint(combinations_wh)
    # print(len(combinations_wh))
    combinations_wh = first_warehouse_combinations(warehouses)
    ######################################################## FILTERING WAREHOUSE COMBINATIONS #########################################

    def filtering_warehouse_combinations(locations_warehouses,combinations_wh):

        # According to distance
        sorted_wh_dist = sorted(locations_warehouses, key = lambda key: locations_warehouses[key]['distance'])
        # print(sorted_wh_dist)


        combinations_wh_copy = copy.deepcopy(combinations_wh)

        combinations_wh_new = []
        for i, wh_comb in enumerate(combinations_wh_copy):

            if len(wh_comb) != 1: 

                if (len(wh_comb) == 2) and (sorted_wh_dist[0] in wh_comb) and (sorted_wh_dist[1] in wh_comb) and (wh_comb not in combinations_wh_new):
                    combinations_wh_new.append(wh_comb)
                
                if (len(wh_comb) == 3 or len(wh_comb) == 4) and (sorted_wh_dist[0] in wh_comb or sorted_wh_dist[1] in wh_comb) and (wh_comb not in combinations_wh_new):
                        combinations_wh_new.append(wh_comb)
                    
                else: 
                    if (len(wh_comb) != 2) and (len(wh_comb) != 3) and (len(wh_comb) != 4):
                        combinations_wh_new.append(wh_comb)

            
        combinations_wh = combinations_wh_new

        return combinations_wh       
    combinations_wh = filtering_warehouse_combinations(locations_warehouses,combinations_wh=combinations_wh)
    return combinations_wh
        
               


# print('---')
# pp.pprint(combinations_wh_new)
# print(f"old has {len(combinations_wh)}")
# print(f"new has {len(combinations_wh_new)}")