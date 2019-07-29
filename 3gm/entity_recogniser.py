from multiprocessing import cpu_count
# Imports
import parser
import collections
import numpy as np
import sys
import pprint
import re
import codifier
import database
import pickle
import string
from spacy import displacy
# spacy
import spacy

# Importing 3gm NER model 
nlp = spacy.load('../models/3gm_ner_model')


sys.path.insert(0, '../resources')
import greek_lemmas


db = database.Database()

def build_greek_stoplist(cnt_swords=300):
    """Builds a list of Greek stopwords"""
    greek_stopwords = []

    with open('../resources/greek_stoplist.dat') as f:
        for i in range(cnt_swords):
            line = f.readline()
            if not line:
                break
            line = line.split(' ')
            greek_stopwords.append(line[0])

    return greek_stopwords

def build_data_samples(min_size=4, use_spacy=True):
    """Returns a list of data samples to be classified"""
    data_samples = []
    indices = {}

    i = 0
    for law in codifier.codifier.laws.keys():
        print(law)
        corpus = codifier.codifier.laws[law].export_law('str')

        data_samples.append(corpus)
        indices[i] = law

        i += 1

    return data_samples, indices


def build_gg_stoplist(data_samples, greek_stopwords, gg_most_common=500):
    words = []
    for x in data_samples:
        words.extend(x.split(' '))
    print('Counting words')

    try:
        counter = pickle.load(open('gg_stoplist.pickle', 'rb'))
    except BaseException:
        counter = collections.Counter(words)
        pickle.dump(counter, open('gg_stoplist.pickle', 'wb'))
    finally:
        for w in counter.most_common(gg_most_common):
            greek_stopwords.append(w[0])
    print('Done Counting')
    return greek_stopwords, words

def displacy_service(text):
    """Deploys a displaCy server in localhost"""
    doc = nlp(text)
    return displacy.parse_deps(doc)

def build_named_entities(use_spacy=True):
    """Detects named entities in a list of laws and saves to database"""
    greek_stopwords = build_greek_stoplist()
    data_samples, indices = build_data_samples(use_spacy=use_spacy)
    greek_stopwords, words = build_gg_stoplist(data_samples, greek_stopwords)

    i = 0
    global db
    db.drop_named_entities()

    for item in data_samples:
         doc = nlp(item)


         entities = []
         for ent in doc.ents:
             entity_tuple = (ent.text, ent.start_char, ent.end_char, ent.label_)
             entities.append(entity_tuple)

         s = {'_id': indices.get(i),
              'entities': entities
          }
         print(s)
         db.named_entities.save(s)
         i+=1


if __name__ == '__main__':
    use_spacy = '--spacy' in sys.argv[1:]
    build_namde_entities(use_spacy=use_spacy)
