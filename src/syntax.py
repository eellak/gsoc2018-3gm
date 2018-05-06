import spacy
from googletrans import Translator
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
from entities import *

# Action Tree Generation

class ActionTreeGenerator:

    '''
        Generate the action tree for a given extract.
        The action tree consists of:
        1. action to do (i.e. add, remove, ammend) as the root of the tree
        2. on what to act (i.e. add a paragraph)
        3. where to do it (i.e. on which law after which section)
    '''
    @staticmethod
    def generate_action_tree(extract, max_what_window = 20):
        global actions
        global whats
        trees = []
        tmp = list(map(lambda s : s.strip(string.punctuation),  extract.split(' ')))
        for action in actions:
            for i, w in enumerate(tmp):
                if action == w:
                    tree = {}
                    tree['root'] = {
                        'id' : i,
                        'action' : action,
                        'children' : []
                    }

                    # find what will be appended

                    w = 1
                    found_what = False
                    for j in range(1, max_what_window + 1):
                        for what in whats:
                            if i + j  <= len(tmp) - 1 and what == tmp[i + j]:
                                print('found ', what)
                                tree['root']['children'].append('what')
                                tree['what'] = {
                                    'id' : i + j,
                                    'context' : what,
                                    'children' : [],
                                }
                                if i + j + 1 <= len(tmp) - 1 and re.search(r'[0-9]', tmp[i + j + 1]) != None:
                                    tree['what']['number'] = tmp[i + j + 1]
                                found_what == True
                                break

                        if found_what:
                            break

                            if i - j >= 0 and what == tmp[i - j]:
                                tree['root']['children'].append('what')
                                tree['what'] = {
                                    'id' : i - j,
                                    'context' : what,
                                    'children' : []
                                }
                                if i - j >= 0 and re.search(r'[0-9]', tmp[i - j + 1]) != None:
                                    tree['what']['number'] = tmp[i - j + 1]
                                found_what = True
                                break

                        if found_what:
                            break

                    # TODO find where clause

                    trees.append(tree)

        return trees


    # Here is something really crazy
    # Translate the sentence to english and then process its syntax with spacy
    @staticmethod
    def translate_and_analyse(extract):

        nlp = spacy.load('en_core_web_lg')
        lemmatizer = spacy.lemmatizer.Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

        translator = Translator()
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
