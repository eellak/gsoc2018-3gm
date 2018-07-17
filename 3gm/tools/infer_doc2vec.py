#!/usr/bin/env python3

# Infer document vectors from trained doc2vec model
# usage: infer_doc2vec.py model.bin docs.txt embeddings.pickle

import gensim.models as g
import codecs
import sys
import pickle
import muliprocessing

def infer(d):
	global m
	global start_alpha
	global infer_epoch
	return tuple(m.infer_vector(d, alpha=start_alpha, steps=infer_epoch))

#parameters
model = sys.argv[1]
test_docs = sys.argv[2]
output_file = sys.argv[3]

#inference hyper-parameters
start_alpha=0.01
infer_epoch=1000
njobs = multiprocessing.cpu_count() - 1
pool = multiprocessing.Pool(njobs)

#load model
m = g.Doc2Vec.load(model)
test_docs = [ x.strip().split() for x in codecs.open(test_docs, "r", "utf-8").readlines() ]

# parallelize jobs using pool
vectors = pool.map(infer, test_docs)

# build lookup
embeddings = {}
for i, d in enumerate(test_docs):
	embeddings[d] = vectors[i]
	embeddings[vectors[i]] = d

# export to dump
pickle.dump(embeddings, open(output_file, "wb"))
