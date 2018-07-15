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
vector_size = 300
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

#enable logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


if tokenize:
	with open(train_corpus, 'r') as f:
		docs = f.read().splitlines()
	docs = nlp_clean(docs)
	docs = [TaggedDocument(doc, [i]) for i, doc in enumerate(docs)]
else:
	docs = g.doc2vec.TaggedLineDocument(train_corpus)


model = g.Doc2Vec(docs, size=vector_size, window=window_size, min_count=min_count, sample=sampling_threshold, workers=worker_count, hs=0, dm=dm, negative=negative_size, dbow_words=1, dm_concat=1, pretrained_emb=None, iter=train_epoch)

#save model
model.save(saved_path)

# infer hyperparams
start_alpha=0.01
infer_epoch=1000

#create embeddings
with open(train_corpus, 'r') as q:
	lines = q.read().splitlines()

if create_embeddings:
	pool = multiprocessing.pool(worker_count)
	vectors = pool.map(infer, lines)
	for d in vectors:
		sys.stdout.write( " ".join([str(x) for x in vector]) + "\n" )
