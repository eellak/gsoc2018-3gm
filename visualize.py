from __future__ import absolute_import, division, print_function
import codecs
import glob
import logging
import multiprocessing
import os
import pprint
import re
import nltk
import sklearn.manifold
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import gensim
from sklearn.cluster import KMeans



def sentence_to_wordlist(raw):
    clean = []
    for words in raw:
        clean.append(words.strip().lower())
        clean = filter(None, clean)
        return clean


def tsne_transform(model, outfile='point.pkl'):
    tsne = sklearn.manifold.TSNE(n_components=2, random_state=0)
    all_word_vectors_matrix = model.wv.syn0
    all_word_vectors_matrix_2d = tsne.fit_transform(all_word_vectors_matrix)# This may take time, depending on Vocab
    points = pd.DataFrame([ (word, coords[0], coords[1])
                            for word, coords in [(word, all_word_vectors_matrix_2d[model.wv.vocab[word].index])
                            for word in model.wv.vocab]
                            ],
                                columns=["word", "x", "y"])
    points.to_pickle(outfile)


def plot_points(filename='point.pkl', N = 50):
    points = pd.read_pickle('point.pkl')
    kmeans = KMeans(n_clusters=5)

    x = points['x'].as_matrix()
    y = points['y'].as_matrix()
    lbl = points['word'].as_matrix()
    pts = []
    for i in range(N):
        pts.append([x[i], y[i]])

        kmeans.fit(pts)
        y_kmeans = kmeans.predict(pts)

        centers = kmeans.cluster_centers_

        plt.figure();
        plt.scatter(x[:N], y[:N], c=y_kmeans, cmap='viridis')
        for i in range(N):
            plt.annotate(lbl[i], xy=(x[i], y[i]))
            plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5);

            plt.show()
]
