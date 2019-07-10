#!/usr/bin/env python3
"""
Train word2vec model and (optionally) create document embeddings for the dataset
In this approach we will try to trainn a model using tensorflow as oposed to 
the gensim implementetion in the 3gm directory
"""
from multiprocessing import cpu_count
import tensorflow as tf
import tokenizer
import numpy as np
import random
import os
import logging
import pickle
import string
import requests
import collections
import io
import tarfile
import urllib.request
import text_helpers
from tensorflow.python.framework import ops
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Embedding, Input, RepeatVector
from keras.optimizers import SGD





def baseline_model():
    model = Sequential()
    model.add(Dense(256, input_dim=Text_INPUT_DIM+Gene_INPUT_DIM*2, init='normal', activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(256, init='normal', activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(80, init='normal', activation='relu'))
    model.add(Dense(9, init='normal', activation="softmax"))
    
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)  
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    return model

# document cleanup


def nlp_clean(data):
    new_data = []
    for d in data:
        new_str = d.lower().strip()
        dlist = tokenizer.tokenizer.split(d, delimiter=' ')
        yield dlist


# doc2vec parameters
batch_size = 500
vocabulary_size = 7500
generations = 100000
model_learning_rate = 0.001
embedding_size = 200  # Word embedding size
doc_embedding_size = 100  # Document embedding size
concatenated_size = embedding_size + doc_embedding_size
num_sampled = int(batch_size / 2)  # Number of negative examples to sample.
window_size = 3  # How many words to consider to the left.

# input corpus
train_corpus = sys.argv[1]

# output model
saved_path = sys.argv[2]

# labels
labels_file = sys.argv[3]


with open(labels_file, 'r') as f:
    labels = f.read().splitlines()

# enable logging
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


taggeddocs = []


with open(train_corpus, 'r') as f:
    docs = f.read().splitlines()


if tokenize:
    docs = nlp_clean(docs)

for label, doc in zip(labels, docs):
    td = TaggedDocument(words=tokenizer.tokenizer.split(
        doc.lower(), delimiter=' '), tags=[label])
    # print(td)
    taggeddocs.append(td)



