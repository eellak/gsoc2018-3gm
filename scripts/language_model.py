from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding, LSTM, Dense, Dropout
from keras.preprocessing.text import Tokenizer
from keras.callbacks import EarlyStopping
from keras.models import Sequential
from keras.utils import np_utils
import keras.utils as ku 
import numpy as np 
import spacy

tokenizer = Tokenizer()

def get_embeddings(vocab):
	return vocab.vectors.data


def create_model(embeddings):
	model = Sequential()
	model.add(Embedding(embeddings.shape[0],embeddings.shape[1],input_length=150,trainable=True,weights=[embeddings],mask_zero=True))
	model.add(LSTM(150, return_sequences = True))
	model.add(Dropout(0.2))
	model.add(LSTM(100))
	model.add(Dense(84, activation='softmax'))

	model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])


	print(model.summary())
	return model 

def generate_text(seed_text, next_words, max_sequence_len):
	for _ in range(next_words):
		token_list = tokenizer.texts_to_sequences([seed_text])[0]
		token_list = pad_sequences([token_list], maxlen=max_sequence_len-1, padding='pre')
		predicted = model.predict_classes(token_list, verbose=1)
		
		output_word = ""
		for word, index in tokenizer.word_index.items():
			if index == predicted:
				output_word = word
				break
		seed_text += " " + output_word
	return seed_text





filename = "20180100009.txt"
raw_text = open(filename).read()
raw_text = raw_text.lower()
# create mapping of unique chars to integers
chars = sorted(list(set(raw_text)))
char_to_int = dict((c, i) for i, c in enumerate(chars))
# summarize the loaded data
n_chars = len(raw_text)
n_vocab = len(chars)
print("Total Characters: ", n_chars)
print("Total Vocab: ", n_vocab)
# prepare the dataset of input to output pairs encoded as integers
seq_length = 150
dataX = []
dataY = []
for i in range(0, n_chars - seq_length, 1):
	seq_in = raw_text[i:i + seq_length]
	seq_out = raw_text[i + seq_length]
	dataX.append([char_to_int[char] for char in seq_in])
	dataY.append(char_to_int[seq_out])
n_patterns = len(dataX)
X = np.reshape(dataX, (n_patterns, seq_length))
# normalize
X = X / float(n_vocab)
# one hot encode the output variable
y = np_utils.to_categorical(dataY)

nlp = spacy.load("blank_vectors")
#nlp.add_pipe(nlp.create_pipe("sentencizer"))
embeddings = get_embeddings(nlp.vocab)
print(len(embeddings))
model = create_model(embeddings)
earlystop = EarlyStopping(monitor='val_loss', min_delta=0, patience=5, verbose=0, mode='auto')
seed_file="20180100009.txt"
seed_text = open(seed_file).read()
model.fit(X, y, epochs=1, verbose=1)
print(generate_text(" Η Ενεργειακή Κοινότητα (Ε.Κοιν.) είναι αστικός συνεταιρισμός αποκλειστικού σκοπού με στόχο την προώθηση της κοινωνικής και αλληλέγγυας οικονομίας, όπως ορίζεται στην παρ. 1 του άρθρου 2 του ν. 4430/2016 ", 3, 151))
