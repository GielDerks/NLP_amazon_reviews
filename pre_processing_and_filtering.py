import numpy as np
import pandas as pd
import ast

#read metadata
data = pd.read_csv("/Users/gielderks/Downloads/metadata.csv", usecols=['categories', 'asin'])


def eval_f(x):
    x = ast.literal_eval(x)
#    print(x)
    return x

def extract_laptop(x):
    x = x[0]
    #print(x)
    for y in x:
       # print(y)
        if y == 'Laptops':
            return 'Laptop'
        else:
            continue
    return

iterate = list(np.arange(1000000, 7000000, 1000000))

for x in iterate:

    print(x)

    path = "/Users/gielderks/PycharmProjects/NLP_V2/laptop_review_data/laptop_metadata" + str(x) + ".csv"

    # load reviews
    data_electronics = pd.read_csv(path, usecols=['asin', 'reviewText', 'overall'])

    # get all product codes
    filter2 = list(data_electronics['asin'])

    #
    data_elec = data[data['asin'].isin(filter2)]

    data_elec= data_elec.dropna()

    data_elec['categories2'] = data_elec['categories'].apply(lambda x: eval_f(x))

    data_elec['Laptop'] = data_elec['categories2'].apply(lambda x: extract_laptop(x))

    only_laptops = data_elec[data_elec['Laptop'] == "Laptop"]

    print(len(only_laptops))

    only_laptops_list = list(only_laptops['asin'])

    data_elec = data_elec[data_elec['asin'].isin(only_laptops_list)]

    data_electronics = data_electronics[data_electronics['asin'].isin(only_laptops_list)]

    path_out = '/Users/gielderks/PycharmProjects/NLP_V2/processed_files/laptop_metadata' + str(x) + ".csv"

    path_out_reviews = '/Users/gielderks/PycharmProjects/NLP_V2/processed_files/laptop_reviews' + str(x) + ".csv"

    data_electronics.to_csv(path_out_reviews)

    data_elec.to_csv(path_out)