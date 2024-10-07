import os
import pandas as pd
from flask import Flask
import ghhops_server as hs



# Register the Hops app as middleware
app = Flask(__name__)
hops = hs.Hops(app)

@hops.component(
    "/gridGen",
    name="gridGen",
    description="Generate a grid",
    icon="logo.png" ,
    inputs=[
        hs.HopsString("Folderpath", "Folder_path", "Path to the beam folder"),
        hs.HopsInteger("Housenumber", "House_number", "The number of the grid you want imported"),
    ],
    outputs=[
        hs.HopsString("Lenths_x", "Len_x", "Lengths of beams in x axis"),
        hs.HopsString("Lenths_y", "Len_y", "Lengths of beams iny axis"),
        hs.HopsString("Depths_x_path", "Depth_x", "Beam x depth path "),
        hs.HopsString("Depths_y_path", "Depth_y", "Beam y depth path "),
        hs.HopsString("Widths_x_path", "Width_x", "Beam x width path "),
        hs.HopsString("Widths_y_path", "Width_y", "Beam y width path "),
        hs.HopsString("Columns dimensions x", "Columns_x", "Size of columns in the x axis"),
        hs.HopsString("Columns simensions y", "Columns_y", "Size of columns in the y axis"),
        hs.HopsString("Tolerance", "Grid tolerance", "Grid size tolerance value")

    ]
)

def gridGen(csv_filepath, Grid):
    Grid = int(Grid)
    # Initialize the result variables
    list_lengths_x = []
    list_lengths_y = []
    depths_x_file_path = ""
    depths_y_file_path = ""
    widths_x_files_path = ""

    try:
        # Construct file paths
        lengths_x_file_path = os.path.join(csv_filepath, 'lengths_dataframe_house_' + str(Grid) + '_x.csv')
        print(lengths_x_file_path)
        lengths_y_file_path = os.path.join(csv_filepath, 'lengths_dataframe_house_' + str(Grid) + '_y.csv')

        depths_x_file_path = os.path.join(csv_filepath, 'depths_dataframe_house_' + str(Grid) + '_x.csv')
        depths_y_file_path = os.path.join(csv_filepath, 'depths_dataframe_house_' + str(Grid) + '_y.csv')
        widths_x_files_path = os.path.join(csv_filepath, 'widths_dataframe_house_' + str(Grid) + '_x.csv')
        widths_y_files_path = os.path.join(csv_filepath, 'widths_dataframe_house_' + str(Grid) + '_y.csv')
        columns_file_path = os.path.join(csv_filepath, 'column_dataframe.csv')
        # Read lengths from CSV files
        df = pd.read_csv(lengths_x_file_path, skiprows=1)
        list_lengths_x = df.iloc[0].tolist()

        df = pd.read_csv(lengths_y_file_path, skiprows=1)
        list_lengths_y = df.iloc[0].tolist()
        
        df = pd.read_csv(columns_file_path)
        columns_dim_x = float(df['x_dim'][0])
        columns_dim_y = float(df['y_dim'][0])
        tolerance = float(df['tolerance'][0])

        
    except Exception as e:
        # Handle the exception (e.g., print the error message)
        print(f"An error occurred: {str(e)}")

    return list_lengths_x, list_lengths_y, depths_x_file_path, depths_y_file_path, widths_x_files_path,widths_y_files_path,columns_dim_x,columns_dim_y,tolerance


if __name__ == "__main__":
    app.run()