import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from main import warehouses
import os

#create base dataframe
index_values = range(50000)
df = pd.DataFrame(index=index_values)

#place variables
density_conc = 2400 #kg/m^3
density_steel = 7840 #kg/m^3
gravity =  9.81 #m/s^2
live_load= 10000 #1000N = 1kN,10kN=10000N
steel_resistance = 1.15
concrete_resistance = 1.50
x = 0.5 # effective depth
cover = 0.07

#ADD GEOMETRY 

def prob_data(mean, cov,distribution):
    #cov is coefficient of variance
    data_array = np.empty(0)
    # while data_array.size < len(index_values):
    if distribution == 'gamma':
        cov = np.sqrt(cov)
        shape = (mean / cov) ** 2
        scale = cov ** 2 / mean
        # Generate random data that follows a gamma distribution
        data = stats.gamma.rvs(a=shape, scale=scale, size=len(index_values))
    elif distribution == 'normal': 
        scale = mean * cov
        data = stats.norm.rvs(loc=mean, scale=scale, size=len(index_values), random_state=None)
    return data

#Add lengths from distribution data
# Specify the parameters
df['lengths'] = prob_data(mean=3.37,cov=0.37, distribution='gamma')  #m
df['depth'] = prob_data(mean=0.48,cov=0.14,distribution='normal') #m
df['concrete_strength'] = prob_data(mean=16.73e6,cov=0.51, distribution='gamma') #N/m^2
df['steel_strength'] = prob_data(mean=371.13e6,cov=0.24,distribution='normal') #N/m^2

# ADD WIDTH , REINFORCEMENT RATIO
df['width'] = np.random.uniform(0.25,0.50,size=len(index_values)) #m
df['reinforcement_ratio'] = np.random.uniform(0.13,4,size=len(index_values)) #% #random numbers between 0.13 and 4 

#CREATE AREA, VOLUME, MASS, WEIGHT, LOAD, COVER, REINFORCEMENT RATIO (%Aconcrete=Asteel)
df['area'] = df['width'] * df['depth']
df['volume'] = df['area'] * df['lengths']
# add explanation for ((100-df['reinforcement_ratio'])/100
df['mass'] = (((100-df['reinforcement_ratio'])/100) * df['volume'] * density_conc)+(((df['reinforcement_ratio'])/100) * df['volume'] * density_steel)#m^3*kg/m^3 =kg
df['weight'] = df['mass'] * gravity #kg* m/s^2 = N
df['load'] = (1.35 * df['weight']) + (1.5*live_load) # dead load = self weight , 1.35* self_weight + 1.5 * live_load #N


# APPLIED BENDING MOMENT, SHEAR LOAD DUE TO SELF_WEIGHT
df['max_moment_due_to_selfweight'] = df['load'] * (df['lengths']) /8 # N*m
df['shear_load_due_to_selfweight'] = df['load']/2 # CHECK with TAHIR
df['area_concrete'] = df['area']*(100-df['reinforcement_ratio'])/100 #m2 * 100-n/100
df['area_steel'] = df['area']*df['reinforcement_ratio']/100


#PLOT DATA
# plt.hist(df['lengths'], density=True, bins=130)  # density=False would make counts
# plt.xlabel('Values')
# plt.ylabel('Frequency')
# plt.title('Original histogram of lengths')
# plt.savefig("Original histogram of lengths.png")

# def plot(column_name,bins): 
#     plt.hist(df[column_name], density=True, bins=bins)  # density=False would make counts
#     plt.xlabel('Values')
#     plt.ylabel('Frequency')
#     plt.title(f'Histogram of {column_name} values')
#     #plt.savefig(f"{column_name}.png")
#     # plt.close()
#     # plt.show()
#     # return



# for i,col_name in enumerate(df.columns):
#     plt.subplot(4,4,i+1)
#     plot(column_name=col_name,bins=130)
# plt.tight_layout()
# plt.savefig(f'subplot_{col_name}.png')
# plt.show()
# plt.close('all')

#FILTER BAD DATA
#delete row if depth < length/12
df = df[abs(df['depth'] - df['lengths'] / 12) < 0.1]
# maybe we should increase the upper threshold so beams can be thicker since their ends woud be cut off so would be stockier
# plt.hist(df['lengths'], density=True, bins=130)  # density=False would make counts
# plt.xlabel('Values')
# plt.ylabel('Frequency')
# plt.title('Histogram of lengths after depth < length/12 ')
# plt.savefig("Histogram of lengths after depth_div_length_12.png")
# plt.show()


#delete rows if moment due to selfweight > 0.167*concrete strength* width*depth^2
df = df[df['max_moment_due_to_selfweight']<(0.167* df['concrete_strength']*df['width']*((df['depth']-cover)**2))] 
# plt.hist(df['lengths'], density=True, bins=130)  # density=False would make counts
# plt.xlabel('Values')
# plt.ylabel('Frequency')
# plt.title('Histogram of lengths after max_moment > 0.167*concrete strength* width*depth^2 ')
# plt.savefig("Histogram of lengths after max_moment_bigger_concrete_strength.png")
# plt.show()

#delete rows if moment due to selfweight > A steel * steel_strength * (1-(0.5*x/d))/gs 
df['x/d'] = (concrete_resistance*df['area_steel']*df['steel_strength'])/ (steel_resistance*0.7*df['concrete_strength']*df['width']*(df['depth'] - cover))
df = df[df['max_moment_due_to_selfweight']<=(df['area']*df['reinforcement_ratio'])*df['steel_strength']* (1-(0.5*df['x/d']))/steel_resistance]
# plt.hist(df['lengths'], density=True, bins=130)  # density=False would make counts
# plt.xlabel('Values')
# plt.ylabel('Frequency')
# plt.title('Histogram of lengths after max _moment <= A steel * steel_strength * (1-(0.5*x/d))/gs ')
# plt.savefig("Histogram of lengths after max _moment_bigger_steel_strength.png")
# plt.show()


# ULTIMATE BENDING MOMENTS

df['ultimate_bending_moment_concrete'] = (0.167* df['concrete_strength']*df['width']*((df['depth']-cover)**2))
df['ultimate_bending_moment_steel'] =(df['area']*df['reinforcement_ratio'])*df['steel_strength']* (1-(0.5*df['x/d']))/steel_resistance


# # Applying a safety factor for over-reinforced beams i.e. ultimate_bending_moment_steel > ultimate_bending_moment_concrete 
# safety_factor = 0.9

# n = 0
# n_change=0
# for i, val in enumerate(df.index):
#     n+=1
#     if df.loc[val,'ultimate_bending_moment_steel']> df.loc[val,'ultimate_bending_moment_concrete']:
#         df.loc[val,'ultimate_bending_moment_steel'] = df.loc[val,'ultimate_bending_moment_steel']*safety_factor
#         df.loc[val,'ultimate_bending_moment_concrete'] = df.loc[val,'ultimate_bending_moment_concrete']*safety_factor
#         n_change+=1
# print(f"{n_change} items out of {n} have been changed")






#ROUND DATAFRAME NUMBERS
#df = df.round(1)
#df = df.applymap(lambda x: round(x, 2) if x.name == 'B' else round(x, 1))
#df = df.applymap(lambda x: round(x, 2) if x == 'area_steel' else round(x, 1))
for column in df.columns:
    if column != 'area_steel':
        df[column] = df[column].apply(lambda x: round(x, 1))
    else:
        df[column] = df[column].apply(lambda x: round(x, 4))


# SET WAREHOUSE 
df['Warehouse'] = np.random.choice(warehouses,len(df)) 


            
df['IDs'] = df.index

df['IDs'] = 'ID_' + df['IDs'].astype(str)

# df = df.set_index('IDs')
#df.index.name = 'IDs'

#SAVE DATAFRAME TO CSV
folder_path_user =  os.path.join(os.getcwd(), "outputs")
df.to_csv(os.path.join(folder_path_user, "Dataframe2.csv"), index=None)

#print(df)
# can you list down all the assumptions you made
# can you make this into a workflow diagram