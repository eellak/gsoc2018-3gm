#!/usr/bin/python
# -*- coding: utf-8 -*-

import tensorflow as tf 
import numpy as np

def transform(txt, words_indices):
 # return np.asarray([char_indices[c] for c in txt], dtype=np.int32)

  result = []
  for char in txt:
    try:
      result.append(words_indices[char])
    except KeyError:
      pass
  return np.array(result, dtype=np.int32)




EMBEDDING_DIM = 512


def lstm_model(seq_len=100, batch_size=None, stateful=True):
  """Language model: predict the next word given the current word."""
  source = tf.keras.Input(
      name='seed', shape=(seq_len,), batch_size=batch_size, dtype=tf.int32)

  embedding = tf.keras.layers.Embedding(input_dim=207813, output_dim=EMBEDDING_DIM)(source)
  lstm_1 = tf.keras.layers.LSTM(EMBEDDING_DIM, stateful=stateful, return_sequences=True)(embedding)
  lstm_2 = tf.keras.layers.LSTM(EMBEDDING_DIM, stateful=stateful, return_sequences=True)(lstm_1)
  lstm_3 = tf.keras.layers.LSTM(EMBEDDING_DIM, stateful=stateful, return_sequences=True)(lstm_2)
  predicted_char = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(207813, activation='softmax'))(lstm_3)
  return tf.keras.Model(inputs=[source], outputs=[predicted_char])

BATCH_SIZE = 5
PREDICT_LEN = 250

# Keras requires the batch size be specified ahead of time for stateful models.
# We use a sequence length of 1, as we will be feeding in one character at a 
# time and predicting the next character.
prediction_model = lstm_model(seq_len=1, batch_size=BATCH_SIZE, stateful=True)
prediction_model.load_weights('lang_generator.h5')

# We seed the model with our initial string, copied BATCH_SIZE times

import json

with open('indices_words.json') as json_file:
    indices_words = json.load(json_file)

with open('words_indices.json') as json_file_2:
    words_indices = json.load(json_file_2)

seed_txt = 'Οι όροι που πρέπει να τηρούνται προκειμένου να  χορηγηθεί η άδεια, είναι οι ακόλουθοι:'
seed_txt = seed_txt.lower()
seed = transform(seed_txt,words_indices)
seed = np.repeat(np.expand_dims(seed, 0), BATCH_SIZE, axis=0)


# First, run the seed forward to prime the state of the model.
prediction_model.reset_states()
for i in range(len(seed) - 1):
  prediction_model.predict(seed[:, i:i + 1])

# Now we can accumulate predictions!
predictions = [seed[:, -1:]]
for i in range(PREDICT_LEN):
  last_word = predictions[-1]
  next_probits = prediction_model.predict(last_word)[:, 0, :]
  
  # sample from our output distribution
  next_idx = [
      np.random.choice(207813, p=next_probits[i])
      for i in range(BATCH_SIZE)
  ]
  predictions.append(np.asarray(next_idx, dtype=np.int32))


for i in range(BATCH_SIZE):
  print('PREDICTION %d\n\n' % i)
  p = [predictions[j][i] for j in range(PREDICT_LEN)]
  print(p)
  generated = ''.join([indices_words[int(c)]+' ' for c in p]) #in p # Convert back to text
  print(generated)
  print()
  #assert len(generated) == PREDICT_LEN, 'Generated text too short'