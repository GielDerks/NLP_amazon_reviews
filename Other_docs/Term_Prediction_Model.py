import pandas as pd

#This is what Python's pickle module is for: it serializes objects so they can be saved to a file,
#and loaded in a program again later on.
import pickle

import spacy


#load spacy model
nlp = spacy.load('en_core_web_lg')

# Parse XML file with annotated laptop reviews
#tree = ET.parse('Laptops_Train.xml')
tree = ET.parse('Restaurants_Train.xml')

root = tree.getroot()