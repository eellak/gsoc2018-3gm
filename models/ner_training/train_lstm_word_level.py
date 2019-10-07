"""
Original found on https://keras.io/examples/lstm_text_generation/
Applying TPU multiprocessing. Deployed in Google Colab.
https://colab.research.google.com/drive/1XdDAGNEZdv16bsPz4U-UmRKQ8evmyuBb
"""
import numpy as np
import tensorflow as tf
import os
import io
import distutils
import collections
from itertools import groupby
import regex as re

import tokenizer

def get_all_words(text):
  counter = 0
  mapping = {}
  inv_mapping = {}
  
  for word in text:
    if not inv_mapping.get(word,None):
      mapping[counter] = word
      inv_mapping[word] = counter
      counter += 1
 
  return inv_mapping, mapping

def split_input_target(chunk):
  input_text = chunk[:-1]
  target_text = chunk[1:]
  return input_text, target_text


if distutils.version.LooseVersion(tf.__version__) < '1.14':
    raise Exception('This notebook is compatible with TensorFlow 1.14 or higher, for TensorFlow 1.13 or lower please use the previous version at https://github.com/tensorflow/tpu/blob/r1.13/tools/colab/shakespeare_with_tpu_and_keras.ipynb')

# This address identifies the TPU we'll use when configuring TensorFlow.
TPU_WORKER = 'grpc://' + os.environ['COLAB_TPU_ADDR']

SHAKESPEARE_TXT = '/content/corpus.txt'

def transform(txt, words_indices):
 # return np.asarray([char_indices[c] for c in txt], dtype=np.int32)

  result = []
  for char in txt:
    try:
      result.append(words_indices[char])
    except KeyError:
      pass
  return np.array(result, dtype=np.int32)



def input_fn(seq_len=100, batch_size=512):
  """Return a dataset of source and target sequences for training."""


  with io.open(SHAKESPEARE_TXT, encoding='utf-8', errors='ignore') as f:
    txt = f.read().lower()
  #txt = txt.replace('. ',' ')
  txt = re.sub(r'\(cid:[0-9]{1,3}\)', '',txt)
  txt = re.sub(r'\\x[a-z0-9]{2}', '',txt)
  my_tokenizer = tokenizer.Tokenizer(exceptions=[])
  tokens = my_tokenizer.split(txt,False, '. ')
  
# txt = [c for c in txt if 0 < ord(c) < 255 or 	894 <= ord(c) <= 974 ]
  
#  with tf.io.gfile.GFile(SHAKESPEARE_TXT,  'r',encoding='ISO-8859-1utf-8') as f:
#    txt = f.read()
  global words_indices
  global indices_words
  words_indices , indices_words  = get_all_words(tokens)
  print(len(words_indices))
  source = tf.constant(transform(tokens,words_indices), dtype=tf.int32)

  ds = tf.data.Dataset.from_tensor_slices(source).batch(seq_len+1, drop_remainder=True)


  BUFFER_SIZE = 10000
  ds = ds.map(split_input_target).shuffle(BUFFER_SIZE).batch(batch_size, drop_remainder=True)

  return ds.repeat()

def lstm_model(seq_len=100, batch_size=None, stateful=True):
  """Language model: predict the next word given the current word."""
  source = tf.keras.Input(
      name='seed', shape=(seq_len,), batch_size=batch_size, dtype=tf.int32)

  embedding = tf.keras.layers.Embedding(input_dim=31099, output_dim=EMBEDDING_DIM)(source)#4881
  lstm_1 = tf.keras.layers.LSTM(EMBEDDING_DIM, stateful=stateful, return_sequences=True)(embedding)
  lstm_2 = tf.keras.layers.LSTM(EMBEDDING_DIM, stateful=stateful, return_sequences=True)(lstm_1)
  predicted_char = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(31099, activation='softmax'))(lstm_2)
  return tf.keras.Model(inputs=[source], outputs=[predicted_char])


tf.keras.backend.clear_session()

resolver = tf.contrib.cluster_resolver.TPUClusterResolver(TPU_WORKER)
tf.contrib.distribute.initialize_tpu_system(resolver)
strategy = tf.contrib.distribute.TPUStrategy(resolver)

with strategy.scope():
  earlystop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=5, verbose=0, mode='auto')
  training_model = lstm_model(seq_len=100, stateful=False)
  training_model.compile(
      optimizer=tf.keras.optimizers.RMSprop(learning_rate=0.01),
      loss='sparse_categorical_crossentropy',
      metrics=['sparse_categorical_accuracy'],
      callbacks=[earlystop])

training_model.fit(
    input_fn(),
    steps_per_epoch=100,
    epochs = 20
)
training_model.save_weights('/tmp/bard.h5', overwrite=True)

import json
with open('words_indices.txt', 'w') as json_file:
  json.dump(words_indices, json_file)

with open('indices words.txt', 'w') as json_file:
  json.dump(indices_words, json_file)
