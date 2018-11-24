import pandas as pd
import numpy as np

iterate = list(np.arange(1000000, 8000000, 1000000))

for x in iterate:


    path_out = '/Users/gielderks/PycharmProjects/NLP_V2/processed_files/laptop_metadata' + str(x) + ".csv"

    path_out_reviews = '/Users/gielderks/PycharmProjects/NLP_V2/processed_files/laptop_reviews' + str(x) + ".csv"

    if x == 1000000:

        metadata = pd.read_csv(path_out)
        reviews = pd.read_csv(path_out_reviews)

    else:

        metadata_add = pd.read_csv(path_out)
        reviews_add = pd.read_csv(path_out_reviews)
        print(len(metadata_add))
        print(len(reviews_add))
        metadata = pd.concat([metadata, metadata_add])
        reviews = pd.concat([reviews, reviews_add])


path_out_reviews = '/Users/gielderks/PycharmProjects/NLP_V2/processed_files/concat_reviews.csv'
metadata = metadata[['asin']]

path_out_metadata = '/Users/gielderks/PycharmProjects/NLP_V2/processed_files/concat_meta.csv'

reviews.to_csv(path_out_reviews, index=False)
metadata.to_csv(path_out_metadata, index=False)