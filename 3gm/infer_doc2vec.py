# infer document vectors from trained doc2vec model
import gensim.models as g
import codecs
import sys
import pickle

#parameters
model= sys.argv[1]
test_docs= sys.argv[2]
output_file= sys.argv[3]

#inference hyper-parameters
start_alpha=0.01
infer_epoch=1000

#load model
m = g.Doc2Vec.load(model)
test_docs = [ x.strip().split() for x in codecs.open(test_docs, "r", "utf-8").readlines() ]

embeddings = {}
for i, d in enumerate(test_docs):
	vector =  m.infer_vector(d, alpha=start_alpha, steps=infer_epoch)
	embeddings[d] = vector

pickle.dump(embeddings, open(output_file, "wb"))

