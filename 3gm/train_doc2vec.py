#!/usr/bin/env python3
# Train word2vec model and (optioanallly) create document embeddings for the dataset
# usage: train_doc2vec.py corpus.txt model.bin labels.txt --tokenize

import gensim.models as g
import logging
import sys
sys.path.insert(0, '../')
import tokenizer
from gensim.models.doc2vec import TaggedDocument
from multiprocessing import cpu_count

# document cleanup
def nlp_clean(data):
	new_data = []
	for d in data:
		new_str = d.lower().strip()
		dlist = tokenizer.tokenizer.split(d, delimiter=' ')
		yield dlist

#doc2vec parameters
vector_size = 150
window_size = 8
min_count = 4
sampling_threshold = 1e-5
negative_size = 5
train_epoch = 50
dm = 0 #0 = dbow; 1 = dmpv
worker_count = cpu_count() - 1
tokenize = '--tokenize' in sys.argv

#input corpus
train_corpus = sys.argv[1]

#output model
saved_path = sys.argv[2]

#labels
labels_file = sys.argv[3]

with open(labels_file, 'r') as f:
	labels = f.read().splitlines()

#enable logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

taggeddocs = []

with open(train_corpus, 'r') as f:
	docs = f.read().splitlines()

if tokenize:
	docs = nlp_clean(docs)

for label, doc in zip(labels, docs):
	td = TaggedDocument(words=tokenizer.tokenizer.split(doc.lower(), delimiter=' '), tags=[label])
	#print(td)
	taggeddocs.append(td)

model = g.Doc2Vec(taggeddocs, size=vector_size, window=window_size, min_count=min_count, sample=sampling_threshold, workers=worker_count, hs=0, dm=dm, negative=negative_size, dbow_words=1, dm_concat=1, pretrained_emb=None, iter=train_epoch)

#save model
model.save(saved_path)
