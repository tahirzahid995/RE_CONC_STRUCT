import pickle

def pickle_open(file_path):
    with open(file_path, 'rb') as file:
        object  = pickle.load(file)
        return object

def dump_into_pickle(file_path,object):

    with open(file_path, 'wb') as file:
        pickle.dump(object, file)