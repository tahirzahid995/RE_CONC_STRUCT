#################################### MAKE COMBINATIONS ON AXIES######################################

import itertools
import numpy as np
import pandas as pd


'''
    # DESCRIPTION: 
    A function which iterates through the available combinations of lengths whose sum should be the length of input axis 
    
    
    # INPUTS:
    
    1.A dictionary whose keys represent groups of data, in our case, groups of beam lengths
    
    dict_list = {
    'B0':{'ID':'N/A', 'SIZE':0, 'LENGTH':0},
    'B1':{'ID':'various B1 codes', 'SIZE':29, 'LENGTH':1},
    'B2':{'ID':'various B2 codes', 'SIZE':52, 'LENGTH':2},
    'B3':{'ID':'various B3 codes', 'SIZE':122, 'LENGTH':3},
    'B4':{'ID':'various B4 codes', 'SIZE':133, 'LENGTH':4},
    'B5':{'ID':'various B5 codes', 'SIZE':30, 'LENGTH':5}
    } 
    
    2.The length of the axis
    
    3. Tolerance of length
    
    # OUTPUTS:
    
    axial_combinations = {
    'y' : [['B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1'], 
           ['B2', 'B2', 'B2', 'B2', 'B2']]
    'x' : [['B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1'],
           ['B2', 'B2', 'B2', 'B2', 'B2', 'B2']] 
    }   
        
'''

#define the column sizes
#for each combination, the length is the length of the combination + the column size

def axial_combinations(axis_length,axis_tolerance,dictionary,column_size):
    
    axis_length = axis_length - column_size
    
    # upper limit and lower limit
    axis_ul = axis_length + axis_tolerance
    axis_ll = axis_length - axis_tolerance


    # Assigning the number of different lengths
    keys = [key for key in dictionary] # B1, B2, B3, B4, B5
    n = len(keys) #5
    # print(keys)
    combinations = []

    # Generate combinations of keys and repetitions from 0 to n
    for r in range(1, n + 1): #check range 1 to 6
        '''  
        CREATE A LOOP THAT CHECKS EACH GROUP 
        in the range of all possible combinations of ('B1,B2,B3,B4,B5', 5) 
        combinations_with_replacement(iterable, r):
        combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC
        First key combination = B1 , out of 1 possible combinations
        then B2 , then B3 and so on until B5
        Then it checks B1 in combination with all the keys so
        B1B1, B1B2 
        same for B2,B3 to B5
        B1B1B1, B1B1B2...B5B5B5
        B1B1B1B1B1...B5B5B5B5B5
        '''
        for key_combination in itertools.combinations_with_replacement(keys, r):
            key_combination = list(key_combination)

            # Calculate the sum of values and update repetitions
            sum_values = 0
            
            ''' 
            FIND THE LENGTH OF THE COMBINATION
            Say Key_combination is B1B2
            first Key = B1
            '''
            for key in key_combination:
                
                '''               
                Sum-values = 0+valueofB1 = 0 + 1 = 1
                key = B2 
                Sum_values = sum_values + valueofB2 = 1 + 2 = 3
                '''
                sum_values += dictionary[key]['LENGTH'] + column_size

                '''            
                Keep on adding the first beam until constraint is satisfied
                the length of the combination is placed into y
                Say that the combination is B1B2B3 , the length will be 1 + 2 + 3 = 6
                '''
                y = sum_values
            '''
            CHECK IF THE LENGTH OF THE COMBINATION FITS INSIDE THE GRID
            Repetitions if itertools.combinations is used instead of itertools.combinations_with_replacement
            How many time does this combination fit into our grid's lengths
            For example B1(=1) fits 11 times insede the 11 meter grid
            say we have the combination B1B12B3, y = 6
            If grid_length (= 11) > y (=6), 
            
            ''' 
            if axis_ll > y:
                while axis_ll > y: 
                    '''
                    y = y + valueoffirst_key
                    so if the combination is B1B2B3
                    y = y + valueofB1 = 6 + 1
                    as it is stil < axis_ll 
                    y = y + valueofB1 = 7 + 1
                    Basically it is y = valuesofB1B2B3 + valueofB1 + valueofB1 +valueofB1 + valueofB1 + valueofB1 = 11
                    '''
                    y += dictionary[key_combination[0]]['LENGTH'] 
                    '''
                    append the combination until it fits inside the grid: 
                    ('B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1', 'B1')
                    If the original combination is B1B2B3
                    Every time that we add one extra valueofB1 above
                    we add at the key combination the extra key
                    so it is B1B2B3.appendB1
                    '''
                    key_combination.append(key_combination[0]) 


                

            #CHECK IF COMBINATION FITS INTO THE TOLERANCES CONTRAINTS
            # Check if the constraint is satisfied
            # if 11 <=B1B2B3B1B1B1B1B1 (=11) <=12 
            #append combination in the list of combinations
            if axis_ll <= y <= axis_ul:
                combinations.append(key_combination)
            
    #  Filters out repetitions
    unique_combinations = []
    for key_combination in combinations:
        if key_combination not in unique_combinations:
            unique_combinations.append(key_combination)

    
    return  unique_combinations







