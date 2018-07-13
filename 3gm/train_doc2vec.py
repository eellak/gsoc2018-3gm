import gensim.models as g
import logging
import multiprocessing
import sys
import tokenizer
from gensim.models.doc2vec import TaggedDocument

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
tokenize = False
create_embeddings = True

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
	with open(sys.argv[3], 'w+') as f:
		for d in lines:
			vector =  model.infer_vector(d, alpha=start_alpha, steps=infer_epoch)
			f.write( " ".join([str(x) for x in vector]) + "\n" )
