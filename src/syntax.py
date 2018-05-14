import spacy
from googletrans import Translator
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
from entities import *
import re
import collections

# Action Tree Generation

class ActionTreeGenerator:
    """
        Generate the action tree for a given extract.
        The action tree consists of:
        1. action to do (i.e. add, remove, ammend) as the root of the tree
        2. on what to act (i.e. add a paragraph)
        3. where to do it (i.e. on which law after which section)
    """

    @staticmethod
    def generate_action_tree(extract, issue, article, max_what_window = 20, max_where_window = 30):
        global actions
        global whats
        trees = []
        tmp = list(map(lambda s : s.strip(string.punctuation),  extract.split(' ')))

        for action in actions:
            for i, w in enumerate(tmp):
                if action == w:
                    tree = collections.defaultdict(dict)
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
                                tree['root']['children'].append('law')
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

                    # If it is a phrase it's located after the word enclosed in quotation marks
                    k = tree['what']['id']

                    print('wut')
                    if tree['what']['context'] == 'παράγραφος':
                        tree['what']['content'] = next(issue.get_extracts(article))

                    found_where = False
                    for j in range(1, max_where_window + 1):
                        for where in wheres:
                            if k + j  <= len(tmp) - 1 and where == tmp[k + j]:
                                tree['root']['children'].append('where')
                                tree['where'] = {
                                    'id' : k + j,
                                    'context' : where,
                                    'children' : [],
                                }
                                found_where == True
                                break

                        if found_where:
                            break

                            if k - j >= 0 and where == tmp[k - j]:
                                tree['root']['children'].append('where')
                                tree['where'] = {
                                    'id' : k - j,
                                    'context' : where,
                                    'children' : []
                                }

                                found_where = True
                                break

                        if found_where:
                            break

                    # EXPERIMENTAL

                    legislative_acts = list ( filter(lambda x : x != [],  [list(re.finditer(date + ' ' + la, extract)) for la in legislative_act]))
                    laws =  list(re.finditer(law_regex, extract))

                    tree['where']['laws'] = laws
                    tree['where']['legislative_acts'] = legislative_acts

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
        roots = []
        for token in doc:
            if token.dep_ == 'ROOT':
                lemma = token.lemma_
                for action in actions:
                    if lemma == action.lemma:
                        roots.append(token)

        for root in roots:
            print ( ActionTreeGenerator.dfs_traversal(root) )


    @staticmethod
    def dfs_traversal(token):
        tree = {}
        stack = [token]


        while stack != []:
            tok = stack.pop()
            tree[tok.text] = tok
            for child in tok.children:
                stack.append(child)

        return tree
