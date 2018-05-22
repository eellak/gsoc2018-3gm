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
                        '_id' : i,
                        'action' : action.__str__(),
                        'children' : []
                    }
                    max_depth = 0

                    # find what will be appended
                    print('Found', action, 'in ', article )

                    w = 1

                    found_what = False
                    for j in range(1, max_what_window + 1):
                        for what in whats:
                            if i + j  <= len(tmp) - 1 and what == tmp[i + j]:
                                tree['root']['children'].append('law')
                                tree['what'] = {
                                    '_id' : i + j,
                                    'context' : what,
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
                                    '_id' : i - j,
                                    'context' : what,
                                }
                                if i - j >= 0 and re.search(r'[0-9]', tmp[i - j + 1]) != None:
                                    tree['what']['number'] = tmp[i - j + 1]
                                found_what = True
                                break

                        if found_what:
                            break

                    # If it is a phrase it's located after the word enclosed in quotation marks
                    k = tree['what']['_id']
                    print('tree what', tree['what']['context'])


                    if tree['what']['context'] == 'παράγραφος':
                        if tree['root']['action'] != 'διαγράφεται':
                            content = next(issue.get_extracts(article))
                            tree['paragraph']['content'] = content
                            tree['what']['content'] = content
                        max_depth = 4

                    elif tree['what']['context'] == 'άρθρο':
                        if tree['root']['action'] != 'διαγράφεται':
                            content = next(issue.get_extracts(article))
                            tree['article']['content'] = content
                            tree['what']['content'] = content
                        max_depth = 3


                    legislative_acts = list ( filter(lambda x : x != [],  [list(re.finditer(date + ' ' + la, extract)) for la in legislative_act]))
                    laws =  list(re.finditer(law_regex, extract))
                    presidential_decrees = list(re.finditer(presidential_decree_regex, extract))
                    laws.extend(presidential_decrees)
                    laws.extend(legislative_acts)


                    # first level are laws
                    tree['law'] = {
                        '_id' : laws[0].group(),
                        'children' : ['article']
                    }

                    #second level is article
                    if max_depth >= 2:
                        articles = list ( filter(lambda x : x != [],  [list(re.finditer(a, extract)) for a in article_regex]))

                        tree['article']['_id'] = articles[0][0].group().split(' ')[1]
                        tree['article']['children'] = ['paragraph'] if max_depth > 2 else []

                    # third level is paragraph
                    if max_depth > 3:
                        paragraph = list ( filter(lambda x : x != [],  [list(re.finditer(a, extract)) for a in paragraph_regex]))

                        tree['paragraph']['_id'] = int(paragraph[0][0].group().split(' ')[1])
                        tree['paragraph']['children'] = ['period'] if max_depth > 4 else []

                    # nest into dictionary
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
    def nest_tree_helper(vertex, tree):
        if tree[vertex] == {}:
            return tree
        if tree[vertex]['children'] == []:
            del tree[vertex]['children']
            return tree
        if len(tree[vertex]['children']) == 1:
            c = tree[vertex]['children'][0]
            del tree[vertex]['children']
            tree[vertex][c] = tree[c]
        ActionTreeGenerator.nest_tree(c, tree)

    @staticmethod
    def nest_tree(vertex, tree):
        ActionTreeGenerator.nest_tree_helper(vertex, tree)


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
