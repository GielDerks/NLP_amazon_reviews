# Laptops are in node 565108
import os
import pandas as pd
import numpy as np
import pickle
from collections import Counter, defaultdict
import re
import matplotlib
from math import pi
import matplotlib.pyplot as plt
import collections
import pickle
import xml.etree.ElementTree as ET
import gensim
import spacy
import pprint
import json

nlp = spacy.load('en_coref_lg')
spacy = nlp

# Load opinion lexicon
neg_file = open("neg_words.txt", encoding="ISO-8859-1")
pos_file = open("pos_words.txt", encoding="ISO-8859-1")
neg = [line.strip() for line in neg_file.readlines()]
pos = [line.strip() for line in pos_file.readlines()]

# create list of postive + negative words
opinion_words = neg + pos

# Get aspects form human annoted reviews
tree = ET.parse('laptop.xml')
root = tree.getroot()

labeled_reviews = []
for sentence in root.findall("sentence"):
    entry = {}
    aterms = []
    aspects = []
    if sentence.find("aspectTerms"):
        for aterm in sentence.find("aspectTerms").findall("aspectTerm"):
            aterms.append(aterm.get("term"))
    if sentence.find("aspectCategories"):
        for aspect in sentence.find("aspectCategories").findall("aspectCategory"):
            aspects.append(aspect.get("category"))
    entry["text"], entry["terms"], entry["aspects"]= sentence[0].text, aterms, aspects
    labeled_reviews.append(entry)
labeled_df = pd.DataFrame(labeled_reviews)

# Create list of aspects mentioned in laptop reviews
aspects_filter = []
for x in labeled_df['terms']:
    for y in x:
        aspects_filter.append(y)

def feature_sentiment(sentence):
    '''
    input: dictionary and sentence
    function: appends dictionary with new features if the feature did not exist previously,
              then updates sentiment to each of the new or existing features
    output: updated dictionary
    '''

    counter_positive = collections.Counter()

    counter_negative = collections.Counter()

    sent_dict = Counter()

    sentence = spacy(sentence)

    for token in sentence:
        # print(sent_dict)

        #    print(token.text,token.dep_, token.head, token.head.dep_)
        # check if the word is an opinion word, then assign sentiment
        if token.text in opinion_words:  # Words such as worked / crashed / well / useless / enjoyed
            #   print(token)

            # print(token.text, 'main_token')
            sentiment = 1 if token.text in pos else -1  # if word is in postive opinion words then add 1 - if in neg opinion words --> substract 1

            # if target is an adverb modifier (i.e. pretty, highly, etc.)
            # but happens to be an opinion word, ignore and pass
            if (token.dep_ == "advmod"):
                # print(token, 'advmod')
                continue
            elif (
                token.dep_ == "amod"):  # adjectical modifier --> amazing lightless of the laptop "amazing is the adjectical mod"

                sent_dict[token.head.text] += sentiment  # important --> amazing is the amod here. Therefore amazing.head = ligthless is added to the dict
                if sentiment > 0:
                    counter_positive[token.head.text] += sentiment
                elif sentiment < 0:
                    counter_negative[token.head.text] += sentiment

            # for opinion words that are adjectives, adverbs, verbs...
            else:

                for child in token.children:  # for example: issues has child many, which is an adjectival modifier
                    # print(child, 'child', child.dep_)
                    # if there's a adj modifier (i.e. very, pretty, etc.) add more weight to sentiment
                    # This could be better updated for modifiers that either positively or negatively emphasize
                    #  if ((child.dep_ == "amod") or (child.dep_ == "advmod")) and (child.text in opinion_words): #does this have to be in opinion words
                    if ((child.dep_ == "amod") or (child.dep_ == "advmod")):  # does this have to be in opinion words
                        sentiment *= 1.5
                        # print(sentiment, token, 'token sentiment')
                    # check for negation words and flip the sign of sentiment  --> double negative e.g. not amazing
                    if child.dep_ == "neg":
                        sentiment *= -1
                        continue

                for child in token.children:

                    # if verb, check if there's a direct object --> lijdend voorwerp in dutch (enjoyed(verb) the keyboard light(direct object))
                    if (token.pos_ == "VERB") & (child.dep_ == "dobj"):

                        sent_dict[child.text] += sentiment
                        if sentiment > 0:
                            counter_positive[token.head.text] += sentiment
                        elif sentiment < 0:
                            counter_negative[token.head.text] += sentiment

                        # check for conjugates (a AND b), then add both to dictionary
                        # Example: Enjoyed both the screen and the keyboard light
                        subchildren = []
                        conj = 0
                        for subchild in child.children:
                            if subchild.text == "and":
                                conj = 1
                            if (conj == 1) and (subchild.text != "and"):
                                subchildren.append(subchild.text)
                                conj = 0
                        for subchild in subchildren:
                            sent_dict[subchild] += sentiment
                            if sentiment > 0:
                                counter_positive[token.head.text] += sentiment
                            elif sentiment < 0:
                                counter_negative[token.head.text] += sentiment

                # check for negation
                for child in token.head.children:
                    if ((child.dep_ == "amod") or (child.dep_ == "advmod")) and (child.text in opinion_words):
                        sentiment *= 1.5
                    # check for negation words and flip the sign of sentiment
                    if (child.dep_ == "neg"):
                        sentiment *= -1

                # check for nouns
                for child in token.head.children:
                    noun = ""
                    if (child.pos_ == "NOUN") and (child.text not in sent_dict):  # OS crashed repeatedly -->
                        noun = child.text
                        # Check for compound nouns
                        for subchild in child.children:
                            if subchild.dep_ == "compound":
                                noun = subchild.text + " " + noun
                        sent_dict[noun] += sentiment
                        if sentiment > 0:
                            counter_positive[token.head.text] += sentiment
                        elif sentiment < 0:
                            counter_negative[token.head.text] += sentiment

    # return sent_dict
    return counter_positive, counter_negative


def replace_pronouns(text):
    text = nlp(text)
    text = text._.coref_resolved
    return text


# load reviews and metadata
reviews = pd.read_csv('laptop_review_data/laptops_reviews.csv')
metadata = pd.read_csv('laptop_review_data/laptop_metadata.csv')

## The code below loops over the laptops reviews and count the negative and postive phrases

unique_laptops = list(metadata['asin'])

output_json = []


outfile = open('laptop_features_test.json', 'w')
outfile.write("[\n")
count2 = 0
length_rtp = len(unique_laptops[0:10])

for laptop in unique_laptops[0:10]:

    print('processed {} out of {} laptops'.format(count2, len(unique_laptops)))

    final_dict = {}
    counter2 = collections.Counter()

    dict_neg_base = {}
    dict_pos_base = {}

    reviews_filtered = reviews[reviews['asin']==laptop]

    reviews_to_process = reviews_filtered['reviewText'][0:10]


    count = 0

    for reviews_f in reviews_to_process:

        count += 1

        try:

            reviews_f = replace_pronouns(reviews_f)

            counter_pos, counter_neg = feature_sentiment(reviews_f)

        except:

            pass

    final_dict = {'name' : laptop, 'positive' : dict(counter_pos), 'negative' : dict(counter_neg)}

    outfile.write(json.dumps(final_dict))
    print(count2, length_rtp)

    if count2 == length_rtp - 1:

        outfile.write("\n")

    else:

        outfile.write(",\n")

    count2 += 1

outfile.write("]")


########################################################################



#
# # Convert dictionaries to pandas dataframe
# df_pos = pd.DataFrame(data={"positive_count": list(dict_pos_base.values())}, index=list(dict_pos_base.keys()))
# df_neg = pd.DataFrame(data={"negative_count": list(dict_neg_base.values())}, index=list(dict_neg_base.keys()))
#
# # Filter on items that are present in the human annoteted reviews
# df_pos = df_pos[df_pos.index.isin(aspects_filter)]
# df_neg = df_neg[df_neg.index.isin(aspects_filter)]
#
# # print(aspects_filter)
# # print(df_pos)
#
# # sort on couter
# df_pos = df_pos.sort_values('positive_count', ascending=False)#[0:10]
#
# df_neg = df_neg.sort_values('negative_count')#[0:10]
# df_neg['negative_count'] = abs(df_neg['negative_count'])
#
# print(df_neg)
# print(df_pos)