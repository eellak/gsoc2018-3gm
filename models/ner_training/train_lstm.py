"""
Original found on https://keras.io/examples/lstm_text_generation/
Applying TPU multiprocessing. Deployed in Google Colab.
"""


from __future__ import print_function
from keras.callbacks import LambdaCallback,EarlyStopping
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.models import model_from_json
from keras.utils.data_utils import get_file
import numpy as np
import random
import sys
import io

path = 'dataset_corpus_A4.txt'
with io.open(path, encoding='utf-8') as f:
    text = f.read().lower()
print('corpus length:', len(text))

chars = sorted(list(set(text)))
print('total chars:', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

# cut the text in semi-redundant sequences of maxlen characters
maxlen = 100
step = 3
sentences = []
next_chars = []
for i in range(0, len(text) - maxlen, step):
    sentences.append(text[i: i + maxlen])
    next_chars.append(text[i + maxlen])
print('nb sequences:', len(sentences))

print('Vectorization...')
x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        x[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1


# build the model: a single LSTM
print('Build model...')
model = Sequential()
model.add(LSTM(128, input_shape=(maxlen, len(chars)),input_dim=2))
model.add(Dense(len(chars), activation='softmax'))

#optimizer = RMSprop(lr=0.01)
#model.compile(loss='categorical_crossentropy', optimizer=optimizer)


def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def on_epoch_end(epoch, _):
    # Function invoked at end of each epoch. Prints generated text.
    print()
    print('----- Generating text after Epoch: %d' % epoch)

    start_index = random.randint(0, len(text) - maxlen - 1)
    for diversity in [0.2, 0.5, 1.0, 1.2]:
        print('----- diversity:', diversity)

        generated = ''
        sentence = text[start_index: start_index + maxlen]
        generated += sentence
        print('----- Generating with seed: "' + sentence + '"')
        sys.stdout.write(generated)

        for i in range(400):
            x_pred = np.zeros((1, maxlen, len(chars)))
            for t, char in enumerate(sentence):
                x_pred[0, t, char_indices[char]] = 1.

            preds = model.predict(x_pred, verbose=0)[0]
            next_index = sample(preds, diversity)
            next_char = indices_char[next_index]

            generated += next_char
            sentence = sentence[1:] + next_char

            sys.stdout.write(next_char)
            sys.stdout.flush()
        print()

print_callback = LambdaCallback(on_epoch_end=on_epoch_end)
earlystop = EarlyStopping(monitor='loss', min_delta=0, patience=2, verbose=0, mode='auto')
#model.fit(x, y,
#          batch_size=128,
#          epochs=30,
#          callbacks=[print_callback,earlystop])

# serialize model to JSON
#model_json = model.to_json()
#with open("model.json", "w") as json_file:
#    json_file.write(model_json)
# serialize weights to HDF5
#model.save_weights("model.h5")
#print("Saved model to disk")

TPU_WORKER = 'grpc://' + os.environ['COLAB_TPU_ADDR']
strategy = tf.distribute.experimental.TPUStrategy(tf.contrib.cluster_resolver.TPUClusterResolver(TPU_WORKER))
"""
import tensorflow as tf
# This address identifies the TPU we'll use when configuring TensorFlow.
TPU_WORKER = 'grpc://' + os.environ['COLAB_TPU_ADDR']
tf.logging.set_verbosity(tf.logging.INFO)

tpu_model = tf.contrib.tpu.keras_to_tpu_model(
    model,
    strategy=tf.distribute.TPUStrategy(
        tf.contrib.cluster_resolver.TPUClusterResolver(TPU_WORKER)))
"""
with strategy.scope():

   tpu_model = tf.keras.Model(model)
   opt = RMSprop(lr=0.01)
   tpu_model.compile(
      optimizer=opt,
      loss='categorical_crossentropy',
      metrics=['loss'])
"""
history = tpu_model.fit(x_train, y_train,
                        epochs=20,
                        batch_size=128 * 8,
                        validation_split=0.2)
"""
tpu_model.save_weights('./tpu_model.h5', overwrite=True)
tpu_model.evaluate(x_test, y_test, batch_size=128 * 8)
