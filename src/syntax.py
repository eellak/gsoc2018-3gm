import spacy
from googletrans import Translator
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
from entities import *

nlp = spacy.load('en_core_web_lg')
lemmatizer = spacy.lemmatizer.Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

translator = Translator()


def translate_and_analyse(extract):
    result = translator.translate(extract, src='el', dest='en').text

    print(extract)
    print(result)

    doc = nlp(result)

    for token in doc:
        if token.dep_ == 'ROOT':
            print(token.text, token.dep_, token.head.text, token.head.pos_,
                  [child for child in token.children])

            lemma = token.lemma_
            print(lemma)
            for action in actions:
                if lemma == action.lemma:
                    print(action)
                    return action
