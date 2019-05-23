import pickle
import json
import os

pickle_filenames = [filename for filename in os.listdir('.') if filename.endswith('.pickle')]
for pickle_filename in pickle_filenames:
    with open(pickle_filename, 'r') as file:
        data = pickle.load(file)
    with open('{}.json'.format(pickle_filename.split('.pickle')[0]), 'w') as json_file:
        json_file.write(json.dumps(data, indent=4, default=str))

