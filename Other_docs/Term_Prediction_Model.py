import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from skmultilearn.problem_transform import LabelPowerset
import numpy as np


nlp = spacy.load('en_coref_lg')

def replace_pronouns(text):
    text = nlp(text)
    text = text._.coref_resolved
    return text

annotated_reviews_df = pd.read_csv('/Users/gielderks/PycharmProjects/NLP_V2/Laptop_Train_Data.csv')

annotated_reviews_df =annotated_reviews_df[0:100]

annotated_reviews_df["text_pro"] = annotated_reviews_df['ReviewText'].map(lambda x: replace_pronouns(x))

# Convert the multi-labels into arrays
mlb = MultiLabelBinarizer()

print('building model')
# use this is categories (aspects) are available in the training data - in the laptop case these are not available
y = mlb.fit_transform(annotated_reviews_df.aspects)

# X[0] =  I charge it at night and skip taking the cord with me because of the good battery life.
# X[0] contains two aspects "cord" and "battery life"
# y[0] becomes a sparse vector where a 1 stand for the available aspects

X = annotated_reviews_df["text_pro"]

# Split data into train and test set
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=0)

# save the the fitted binarizer labels
# This is important: it contains how the multi-label was binarized, so you need to
# load this in the next folder in order to undo the transformation for the correct labels.
filename = 'mlb.pkl'
pickle.dump(mlb, open(filename, 'wb'))


# LabelPowerset allows for multi-label classification
# Multi-label classification is the supervised classification task where
# each data instance may be associated with multiple class labels.
# Build a pipeline for multinomial naive bayes classification
# Label Powerset (LP): every labelset is a single class-label in a multi-class problem
text_clf = Pipeline([('vect', CountVectorizer(stop_words = "english",ngram_range=(1, 1))),
                     ('tfidf', TfidfTransformer(use_idf=False)),
                     ('clf', LabelPowerset(MultinomialNB(alpha=1e-1))),])


#This explains how pipelines work: https://www.kaggle.com/baghern/a-deep-dive-into-sklearn-pipelines

text_clf = text_clf.fit(X_train, y_train)
predicted = text_clf.predict(X_test)
print(predicted)

# Calculate accuracy
print(np.mean(predicted == y_test))



