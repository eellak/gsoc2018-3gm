import spacy
from googletrans import Translator
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
from entities import *

nlp = spacy.load('en_core_web_lg')
lemmatizer = spacy.lemmatizer.Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

extracts = ['Μετά το άρθρο 9Α του ν. 4170/2013, που προστέθηκε με το άρθρο 3 του ν. 4474/2017, αντικαθίσταται άρθρο 9ΑΑ, ως εξής',
'''Στο τέλος του άρθρου 5 της από 24.12.1990 Πράξης Νομοθετικού Περιεχομένου «Περί Μουσουλμάνων Θρησκευτικών Λειτουργών» (Α΄182) που κυρώθηκε με το άρθρο μόνο του ν. 1920/1991 (Α΄11) προστίθεται παράγραφος 4 ως εξής''']
translator = Translator()

for extract in extracts:
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
                    break
