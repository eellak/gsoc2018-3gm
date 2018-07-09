from entities import *
import re
import collections
import logging
import helpers
import tokenizer
import itertools
import copy

try:
    import spacy
    from spacy import displacy
    import el_unnamed
    nlp = el_unnamed.load()
except ImportError:
    pass



class UncategorizedActionException(Exception):
    """This exception is raised whenever an action cannot be
    classified.
    """

    def __init__(self, s):
        self.message = 'Uncategorized Action: {}'.format(s)
        super().__init__(self.message)

    __str__ = lambda self: self.message
    __repr__ = lambda self: self.message


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
    def get_latest_statute(statutes):
        """Returns latest statute in a given list of
        statutes by first splitting the statutes and then
        finding the one with the latest year
        """
        statutes_ = [re.split(r'[/ .]', statute)[-1] for statute in statutes]
        latest = None
        latest_statute = None
        for i, s in enumerate(statutes_):
            if s.isdigit():
                if not latest or latest <= int(s):
                    latest = int(s)
                    latest_statute = statutes[i]
        if not latest:
            return statutes[0]

        return latest_statute

    @staticmethod
    def detect_latest_statute(extract):
        legislative_acts = list(re.finditer(legislative_act_regex, extract))
        laws =  list(re.finditer(law_regex, extract))
        presidential_decrees = list(re.finditer(presidential_decree_regex, extract))
        legislative_decrees = list(re.finditer(legislative_decree_regex, extract))

        laws.extend(presidential_decrees)
        laws.extend(legislative_acts)
        laws.extend(legislative_decrees)


        laws = [law.group() for law in laws]

        print('Laws are', laws)


        law = ActionTreeGenerator.get_latest_statute(laws)

        return law


    @staticmethod
    def generate_action_tree(extract, issue, article, nested=True, max_what_window = 20, max_where_window = 30):
        global actions
        global whats
        trees = []
        print('Candidate Extract is')
        print(extract)
        tmp = list(map(lambda s : s.strip(string.punctuation),  extract.split(' ')))
        print(tmp)

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


                    logging.info('Found ' + str(action) + ' in ' + article )

                    found_what = False
                    for j in range(1, max_what_window + 1):
                        for what in whats:
                            if i + j  <= len(tmp) - 1 and what == tmp[i + j]:
                                tree['root']['children'].append('law')
                                tree['what'] = {
                                    'index' : i + j,
                                    'context' : what,
                                }
                                if i + j + 1 <= len(tmp) - 1 and re.search(r'[0-9]', tmp[i + j + 1]) != None:
                                    tree['what']['number'] = tmp[i + j + 1]
                                else:
                                    tree['what']['number'] = None

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
                                else:
                                    tree['what']['number'] = None
                                found_what = True
                                break

                        if found_what:
                            break

                    if found_what:
                        print('What')
                        print('Subject is', tree['what'])



                    # TODO fix numeral if full

                    # If it is a phrase it's located after the word enclosed in quotation marks
                    k = tree['what']['index']

                    extract_generator = issue.get_extracts(article)

                    if tree['what']['context'] in ['παράγραφος', 'παράγραφοι']:
                        if tree['root']['action'] != 'διαγράφεται':
                            content = next(extract_generator)
                            tree['paragraph']['content'] = content
                            tree['what']['content'] = content
                        max_depth = 4

                    elif tree['what']['context'] == 'άρθρο':
                        if tree['root']['action'] != 'διαγράφεται':
                            content = next(extract_generator)
                            tree['article']['content'] = content
                            tree['what']['content'] = content
                        max_depth = 3
                    elif tree['what']['context'] == 'εδάφιο':
                        content = next(extract_generator)

                        tree['what']['content'] = content
                    elif tree['what']['context'] == 'φράση':
                        # TODO more epxressions for detection
                        # TODO separate phrases from paragraphs and articles so they always exist in extracts



                        location = 'end'
                        # get old phrase
                        before_phrase = re.search(' μετά τη φράση «', extract)
                        after_phrase = re.search(' πριν τη φράση «', extract)
                        old_phrase = None
                        if before_phrase or after_phrase:
                            if before_phrase:
                                start_of_phrase = before_phrase.span()[1]
                                end_of_phrase = re.search('»', extract[start_of_phrase:]).span()[0] + start_of_phrase
                                location = 'before'
                                old_phrase = extract[start_of_phrase: end_of_phrase]
                            elif after_phrase:
                                start_of_phrase = after_phrase.span()[1]
                                end_of_phrase = re.search('»', extract[start_of_phrase:]).span()[0]
                                location = 'after'
                                old_phrase = extract[start_of_phrase: end_of_phrase]

                        new_phrase = None
                        phrase_index = re.search(' η φράση(|,) «', extract)

                        if phrase_index:
                            start_of_phrase = phrase_index.span()[1]
                            end_of_phrase = re.search('»', extract[start_of_phrase:]).span()[0] + start_of_phrase
                            new_phrase = extract[start_of_phrase + 2: end_of_phrase - 2]

                        if old_phrase and new_phrase:
                            tree['what']['location'] = location
                            tree['what']['old_phrase'] = old_phrase
                            tree['what']['new_phrase'] = new_phrase
                            tree['what']['content'] = new_phrase



                    law = ActionTreeGenerator.detect_latest_statute(extract)

                    # first level are laws
                    tree['law'] = {
                        '_id' : law,
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
                        try:
                            ActionTreeGenerator.nest_tree('root', tree)
                            trees.append(tree)
                        except:
                            pass


        return trees

    @staticmethod
    def generate_action_tree_from_string(s, nested=True, max_what_window = 20, max_where_window = 30):
        global actions
        global whats

        trees = []

        # get extracts and non-extracts using helper functions
        extracts, non_extracts = helpers.get_extracts(s)

        print(extracts)

        print(non_extracts)

        print('Joining non_extracts')

        non_extracts = ' '.join(non_extracts)

        print(non_extracts)

        print('Splitting with tokenizer')

        non_extracts = tokenizer.tokenizer.split(non_extracts, delimiter='. ')

        print(non_extracts)

        extract_cnt = 0


        for non_extract in non_extracts:

            doc = nlp(non_extract)

            tmp = list(map(lambda s : s.strip(string.punctuation),  non_extract.split(' ')))
            print(tmp)

            for action in actions:
                for i, w in enumerate(doc):
                    if action == w.text:
                        tree = collections.defaultdict(dict)
                        tree['root'] = {
                            '_id' : i,
                            'action' : action.__str__(),
                            'children' : []
                        }
                        max_depth = 0


                        logging.info('Found ' + str(action))

                        if str(action) not in ['διαγράφεται', 'παύεται']:
                            extract = extracts[extract_cnt]
                            extract_cnt += 1


                        found_what, tree, is_plural = ActionTreeGenerator.get_nsubj(doc, i, tree)
                        if found_what:
                            k = tree['what']['index']
                            if tree['what']['context'] not in ['φράση', 'φράσεις']:
                                tree['what']['number'] = list(helpers.ssconj_doc_iterator(doc, k, is_plural))

                        else:
                            found_what, tree, is_plural = ActionTreeGenerator.get_nsubj_fallback(tmp, i, tree)


                        # get content
                        tree, max_depth = ActionTreeGenerator.get_content(tree, extract)

                        # split to subtrees
                        subtrees = ActionTreeGenerator.split_tree(tree)

                        # iterate over subtrees
                        for subtree in subtrees:

                            # get latest statute
                            law = ActionTreeGenerator.detect_latest_statute(non_extract)

                            # first level are laws
                            subtree['law'] = {
                                '_id' : law,
                                'children' : ['article']
                            }

                            #second level is article
                            if max_depth >= 2:
                                articles = list ( filter(lambda x : x != [],  [list(re.finditer(a, non_extract)) for a in article_regex]))
                                subtree['article']['_id'] = articles[0][0].group().split(' ')[1]
                                subtree['article']['children'] = ['paragraph'] if max_depth > 2 else []

                            # third level is paragraph
                            if max_depth > 3:

                                paragraph = list ( filter(lambda x : x != [],  [list(re.finditer(a, non_extract)) for a in paragraph_regex]))
                                subtree['paragraph']['_id'] = int(paragraph[0][0].group().split(' ')[1])

                                subtree['paragraph']['children'] = ['period'] if max_depth > 4 else []

                            # nest into dictionary
                            if nested:
                                try:
                                    ActionTreeGenerator.nest_tree('root', subtree)

                                    trees.append(subtree)

                                except:
                                    pass


        return trees


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
    def get_nsubj(doc, i, tree):
        global whats
        found_what = False
        root_token = doc[i]
        for child in root_token.children:

            if child.dep_ in ['nsubj', 'obl']:
                for what in whats:
                    if child.text == what:
                        found_what = True
                        tree['root']['children'].append('law')
                        tree['what'] = {
                            'index' : child.i,
                            'context' : what,
                        }
                        logging.info('nlp ok')

                        is_plural =  helpers.is_plural(what)

                        return found_what, tree, is_plural

        return found_what, tree, False

    @staticmethod
    def get_nsubj_fallback(tmp, tree, i):
        found_what = False
        logging.info('Fallback mode')
        for j in range(1, max_what_window + 1):
            for what in whats:
                if i + j  <= len(tmp) - 1 and what == tmp[i + j]:
                    tree['root']['children'].append('law')
                    tree['what'] = {
                        'index' : i + j,
                        'context' : what,
                    }

                    if i + j + 1 <= len(tmp) - 1 and re.search(r'[0-9]', tmp[i + j + 1]) != None:
                        tree['what']['number'] = tmp[i + j + 1]
                    else:
                        tree['what']['number'] = None

                    is_plural = helpers.is_plural(what)
                    return found_what, tree, is_plural

                if i - j >= 0 and what == tmp[i - j]:
                    tree['root']['children'].append('law')
                    tree['what'] = {
                        'index' : i - j,
                        'context' : what,
                    }
                    if i - j >= 0 and re.search(r'[0-9]', tmp[i - j + 1]) != None:
                        tree['what']['number'] = tmp[i - j + 1]
                    else:
                        tree['what']['number'] = None

                    is_plural = helpers.is_plural(what)
                    return found_what, tree, is_plural

        return found_what, tree, False

    @staticmethod
    def get_rois_from_extract(q, what, idx_list):
        queries = []
        for idx in idx_list:
            if what in ['παράγραφος', 'παράγραφοι']:
                x = idx + '. '
            elif what in ['άρθρο', 'άρθρα']:
                x = 'Άρθρο ' + idx
            elif what in ['περίπτωση', 'περιπτώσεις', 'υποπερίπτωση', 'υποπεριπτώσεις']:
                x = idx + ') '
            queries.append(x)

        spans = []
        for x in queries:
            match = re.search(x, q)
            if match:
                spans.append(match.span()[0])
        spans.append(len(q))
        spans.sort()

        result = []
        for i in range(len(spans) - 1):
            start = spans[i]
            end = spans[i+1]
            result.append(q[start:end])

        return result

    @staticmethod
    def split_tree(tree):
        idx_list = tree['what']['number']
        extract = tree['what']['content']
        what = tree['what']['context']

        if len(idx_list) == 1:
            tree['what']['number'] = idx_list[0]
            result = [tree]

        else:
            result = []
            contents = ActionTreeGenerator.get_rois_from_extract(extract, what, idx_list)
            for idx, s in itertools.zip_longest(idx_list, contents):
                tmp = copy.deepcopy(tree)
                tmp['what']['number'] = idx
                tmp['what']['content'] = s
                result.append(tmp)

        return result

    @staticmethod
    def get_content(tree, extract):
        max_depth = 0

        if tree['what']['context'] in ['άρθρο', 'άρθρα']:
            if tree['root']['action'] != 'διαγράφεται':
                content = extract
                tree['article']['content'] = content
                tree['what']['content'] = content
            max_depth = 3

        elif tree['what']['context'] in ['παράγραφος', 'παράγραφοι']:
            if tree['root']['action'] != 'διαγράφεται':
                content = extract
                tree['paragraph']['content'] = content
                tree['what']['content'] = content
            max_depth = 4

        elif tree['what']['context'] in ['εδάφιο', 'εδάφια']:
            if tree['root']['action'] != 'διαγράφεται':
                content = extract
                tree['what']['content'] = content
            max_depth = 5

        elif tree['what']['context'] in ['φράση', 'φράσεις']:
            location = 'end'
            max_depth = 6

            # get old phrase
            before_phrase = re.search(' μετά τη φράση «', s)
            after_phrase = re.search(' πριν τη φράση «', s)
            old_phrase = None
            if before_phrase or after_phrase:
                if before_phrase:
                    start_of_phrase = before_phrase.span()[1]
                    end_of_phrase = re.search('»', s[start_of_phrase:]).span()[0] + start_of_phrase
                    location = 'before'
                    old_phrase = s[start_of_phrase: end_of_phrase]
                elif after_phrase:
                    start_of_phrase = after_phrase.span()[1]
                    end_of_phrase = re.search('»', s[start_of_phrase:]).span()[0]
                    location = 'after'
                    old_phrase = s[start_of_phrase: end_of_phrase]

            new_phrase = None
            phrase_index = re.search(' η φράση(|,) «', s)

            if phrase_index:
                start_of_phrase = phrase_index.span()[1]
                end_of_phrase = re.search('»', s[start_of_phrase:]).span()[0] + start_of_phrase
                new_phrase = s[start_of_phrase + 2: end_of_phrase - 2]

            if old_phrase and new_phrase:
                tree['what']['location'] = location
                tree['what']['old_phrase'] = old_phrase
                tree['what']['new_phrase'] = new_phrase
                tree['what']['content'] = new_phrase

        return tree, max_depth

    @staticmethod
    def detect_from_regex(non_extract, regex):
        roi = list ( filter(lambda x : x != [],  [list(re.finditer(a, non_extract)) for a in regex]))
        return int(paragraph[0][0].group().split(' ')[1])

    @staticmethod
    def detect_with_iterator(non_extract_split, words):
        for i, w in enumerate(non_extract_split):
            if w in words:
                try:
                    iters = list(helpers.ssconj_doc_iterator(non_extract_split, i))
                    return iters[0]
                except:
                    continue    
