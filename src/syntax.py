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
    def generate_action_tree(extract, issue, article, nested=True, max_what_window = 20, max_where_window = 30):
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
                        'action' : action.__str__(),
                        'children' : []
                    }
                    max_depth = 0

                    # find what will be appended

                    w = 1

                    found_what = False
                    for j in range(1, max_what_window + 1):
                        for what in whats:
                            if i + j  <= len(tmp) - 1 and what == tmp[i + j]:
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
                                tree['root']['children'].append('law')
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

                    if tree['what']['context'] == 'παράγραφος':
                        tree['paragraph'] = {}
                        tree['paragraph']['content'] = next(issue.get_extracts(article))
                        max_depth = 4

                    elif tree['what']['context'] == 'άρθρο':
                        tree['article']['content'] = next(issue.get_extracts(article))
                        max_depth = 3


                    legislative_acts = list ( filter(lambda x : x != [],  [list(re.finditer(date + ' ' + la, extract)) for la in legislative_act]))
                    laws =  list(re.finditer(law_regex, extract))



                    # first level are laws
                    tree['law'] = {
                        'id' : laws[0].group(),
                        'children' : ['article']
                    }

                    #second level is article
                    if max_depth >= 2:
                        articles = list ( filter(lambda x : x != [],  [list(re.finditer(a, extract)) for a in article_regex]))

                        tree['article']['id'] = int(articles[0][0].group().split(' ')[1])
                        tree['article']['children'] = ['paragraph'] if max_depth > 2 else []

                    #third level is paragraph
                    if max_depth >= 3:
                        paragraph = list ( filter(lambda x : x != [],  [list(re.finditer(a, extract)) for a in paragraph_regex]))

                        tree['paragraph']['id'] = int(paragraph[0][0].group().split(' ')[1])
                        tree['paragraph']['children'] = ['period'] if max_depth > 4 else []


                    if nested:
                        ActionTreeGenerator.nest_tree('root', tree)


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
    def nest_tree(vertex, tree):
        if tree[vertex] == {} or len(tree[vertex]['children']) == 0:
            return tree
        if len(tree[vertex]['children']) == 1:
            c = tree[vertex]['children'][0]
            del tree[vertex]['children']
            tree[vertex][c] = tree[c]
        ActionTreeGenerator.nest_tree(c, tree)



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
