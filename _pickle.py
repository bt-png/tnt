import pickle


# TO SAVE ANY OBJECT (source_object_name) AS A PICKLE FILE...
def save():
    with open('../directory_name/source_object_name.pkl', 'wb') as f:
        pickle.dump(object_name, f)


# TO UPLOAD ANY PICKLE FILE INTO AN OBJECT (dest_object_name)...
def read():
    with open('../directory_name/source_object_name.pkl', 'rb') as f:
        dest_object_name = pickle.load(f)