from multiprocessing import cpu_count

# sklearn
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import NMF, LatentDirichletAllocation

# Imports
from helpers import connected_components, get_edges
import parser
import collections
import numpy as np
import sys
import pprint
import re
import codifier
import database
import math
import pickle
import string
from spacy import displacy
# spacy
import spacy
try:
    import el_small
    nlp = el_small.load(max_length=2000000)
except:
    import el_core_web_sm
    nlp = el_core_web_sm.load(max_length=2000000)

sys.path.insert(0, '../resources')
import greek_lemmas


db = database.Database()


def contains_digit_or_num(i): return any(
    j.isdigit() or j in string.punctuation for j in i)



def build_greek_stoplist(cnt_swords=300):
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
    data_samples = []
    indices = {}

    i = 0
    for law in codifier.codifier.laws.keys():
        print(law)
        corpus = codifier.codifier.laws[law].export_law('str')
        if use_spacy:
            tmp = nlp(corpus)
        else:
            tmp = corpus.split(' ')
        corpus = []
        for j, word in enumerate(tmp):
            if contains_digit_or_num(word.text) or len(word.text) < min_size:
                continue
            try:
                if use_spacy:
                    try:
                        corpus.append(greek_lemmas[word.lemma_])
                    except BaseException:
                        corpus.append(greek_lemmas[word])
                else:
                    corpus.append(greek_lemmas[word])
            except BaseException:
                corpus.append(str(word))

        corpus = ' '.join(corpus)

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
    doc = nlp(text)
    return displacy.parse_deps(doc)

def build_entity_recogniser(use_spacy=True):
    greek_stopwords = build_greek_stoplist()
    data_samples, indices = build_data_samples(use_spacy=use_spacy)
    greek_stopwords, words = build_gg_stoplist(data_samples, greek_stopwords)

    # Initial Parameters
    n_samples = len(data_samples)  # Len of data samples

    doc = nlp(data_samples)

    pickle.dump(nlp, open('ner.pickle', 'wb'))



if __name__ == '__main__':
    use_spacy = '--spacy' in sys.argv[1:]
    build_topics(use_spacy=use_spacy)
