from flask import Flask
from flask import request
import spacy
#import en_core_web_lg
import json

#load spacy models
nlp = spacy.load('en')
from collections import Counter

# Load opinion lexicon
neg_file = open("neg_words.txt", encoding="ISO-8859-1")
pos_file = open("pos_words.txt", encoding="ISO-8859-1")
neg = [line.strip() for line in neg_file.readlines()]
pos = [line.strip() for line in pos_file.readlines()]

# create list of postive + negative words
opinion_words = neg + pos

spacy = nlp
app = Flask(__name__)

@app.route("/feature_sentiment/", methods=['GET'])
def feature_sentiment():
    '''
    input: dictionary and sentence
    function: appends dictionary with new features if the feature did not exist previously,
              then updates sentiment to each of the new or existing features
    output: updated dictionary
    '''

    sentence = request.args.get('sentence')

    sent_dict = Counter()
    sentence = spacy(sentence)

    debug = 0
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

                sent_dict[
                    token.head.text] += sentiment  # important --> amazing is the amod here. Therefore amazing.head = ligthless is added to the dict

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
    sent_dict = json.dumps(dict(sent_dict))
    print(type(sent_dict))
    return sent_dict

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 9000, app)

# example
# http://localhost:9000/parse/?sentence=I like apples and especially the red ones
# http://localhost:9000/feature_sentiment/?sentence=I like apples and especially the red ones
