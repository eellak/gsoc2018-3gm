#!/usr/bin/env python3
# Label embedding description
# usage: label_embeddings.py labels.txt output.pickle < embeddings.txt
import sys
import pickle

embeddings_txt = sys.stdin.read().splitlines()
label_file = sys.argv[1]
output = sys.argv[2]
with open(label_file) as f:
    labels = f.read().splitlines()

embeddings = {}

for emb, lbl in zip(embeddings_txt, labels):
    emb = tuple([float(x) for x in emb.split(' ')])
    embeddings[lbl] = emb
    embeddings[emb] = lbl

pickle.dump(embeddings, open(output, 'wb'))
