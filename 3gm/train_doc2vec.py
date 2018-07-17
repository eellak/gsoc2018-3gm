#!/usr/bin/env python3
# Train word2vec model and (optioanallly) create document embeddings for the dataset
# usage: train_doc2vec.py corpus.txt model.bin --embeddings --tokenize > embeddings.txt
# or (with labeling): train_doc2vec.py corpus.txt model.bin --embeddings --tokenize | label_embeddings.py labels.txt output.pickle

import gensim.models as g
import logging
import multiprocessing
import sys
import tokenizer
from gensim.models.doc2vec import TaggedDocument
from infer_doc2vec import infer

# document cleanup
def nlp_clean(data):
	new_data = []
	for d in data:
		new_str = d.lower()
		dlist = tokenizer.tokenizer.split(d, delimiter='. ')
		new_data.append(dlist)
	return new_data

#doc2vec parameters
vector_size = 150
window_size = 15
min_count = 1
sampling_threshold = 1e-5
negative_size = 5
train_epoch = 100
dm = 0 #0 = dbow; 1 = dmpv
worker_count = multiprocessing.cpu_count() - 1
tokenize = '--tokenize' in sys.argv
create_embeddings = '--embeddings' in sys.argv

#input corpus
train_corpus = sys.argv[1]

#output model
saved_path = sys.argv[2]

#labels
labels_file = sys.argv[3]

with open(labels_file) as f:
	labels = f.read().splitlines()

#enable logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

docs = []

if tokenize:
	with open(train_corpus, 'r') as f:
		docs = f.read().splitlines()
	docs = nlp_clean(docs)

for label, doc in zip(labels, docs):
    td = TaggedDocument(words=line.split(), tags=[label])
    docs.append(td)

# model = g.Doc2Vec(window=8, dm = 0, hs=0, min_count=2, alpha=0.1, size=200, min_alpha=0.0001, epochs=50, workers=6, sample=1e-5, dbow_words=1, negative=5)

model = g.Doc2Vec(size=vector_size, window=window_size, min_count=min_count, sample=sampling_threshold, workers=worker_count, hs=0, dm=dm, negative=negative_size, dbow_words=1, dm_concat=1, pretrained_emb=None, iter=train_epoch)
model.build_vocab(docs)
model.train(docs, total_examples=model.corpus_count, epochs=model.iter)

#save model
model.save(saved_path)
