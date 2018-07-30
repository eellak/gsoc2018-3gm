import entities
import re
import collections
import logging
import helpers
import tokenizer
import itertools
import copy
import string
import phrase_fun


import spacy
import el_small
nlp = el_small.load()


class UncategorizedActionException(Exception):
    """This exception is raised whenever an action cannot be
    classified.
    """

    def __init__(self, s):
        self.message = 'Uncategorized Action: {}'.format(s)
        super().__init__(self.message)

    def __str__(self): return self.message

    def __repr__(self): return self.message


# Action Tree Generation

class ActionTreeGenerator:
    """
            Generate the action tree for a given extract.
            The action tree consists of:
            1. action to do (i.e. add, remove, ammend) as the root of the tree
            2. on what to act (i.e. add a paragraph)
            3. where to do it (i.e. on which law after which section)
    """

    def __call__(self, s):
        return ActionTreeGenerator.generate_action_tree_from_string(s)

    trans_lookup = {
        'άρθρ': 'article',
        'παράγραφ': 'paragraph',
        'παρ.': 'paragraph',
        'εδάφ': 'period',
        'φράσ': 'phrase',
        'περίπτωσ': 'case',
        'υποπερίπτωσ': 'subcase'
    }

    children_loopkup = {
        'law': ['article'],
        'article': ['paragraph'],
        'paragraph': ['period', 'case'],
        'period': ['phrase'],
        'case': ['subcase'],
        'subcase': [],
        'phrase': []
    }

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
        legislative_acts = list(
            re.finditer(
                entities.legislative_act_regex,
                extract))
        laws = list(re.finditer(entities.law_regex, extract))
        presidential_decrees = list(re.finditer(
            entities.presidential_decree_regex, extract))
        legislative_decrees = list(
            re.finditer(
                entities.legislative_decree_regex,
                extract))

        laws.extend(presidential_decrees)
        laws.extend(legislative_acts)
        laws.extend(legislative_decrees)

        laws = [law.group() for law in laws]

        logging.info('Laws are', laws)

        law = ActionTreeGenerator.get_latest_statute(laws)

        return law

    @staticmethod
    def generate_action_tree_from_string(
            s,
            nested=False,
            max_what_window=20,
            max_where_window=30,
            use_regex=False):

        # results are stored here

        trees = []
        # fix par abbrev
        s = helpers.fix_par_abbrev(s)

        # get extracts and non-extracts using helper functions
        parts = tokenizer.tokenizer.split(s, False, '. ')
        extracts, non_extracts = helpers.get_extracts(s)

        non_extracts = ' '.join(non_extracts)
        non_extracts = tokenizer.tokenizer.split(non_extracts, True, '. ')

        extract_cnt = 0

        for part_cnt, non_extract in enumerate(non_extracts):

            doc = nlp(non_extract)

            tmp = list(map(lambda s: s.strip(
                string.punctuation), non_extract.split(' ')))

            for action in entities.actions:
                for i, w in enumerate(doc):
                    if action == w.text:
                        tree = collections.defaultdict(dict)
                        tree['root'] = {
                            '_id': i,
                            'action': action.__str__(),
                            'children': []
                        }
                        max_depth = 0

                        logging.info('Found ' + str(action))

                        extract = None
                        if str(action) not in [
                                'διαγράφεται', 'παύεται', 'καταργείται']:
                            try:
                                extract = extracts[extract_cnt]
                                extract_cnt += 1
                            except IndexError:
                                extract = None

                        found_what, tree, is_plural = ActionTreeGenerator.get_nsubj(
                            doc, i, tree)
                        if found_what:
                            k = tree['what']['index']
                            if tree['what']['context'] not in [
                                    'φράση', 'φράσεις', 'λέξη', 'λέξεις']:
                                tree['what']['number'] = list(
                                    helpers.ssconj_doc_iterator(doc, k, is_plural))
                            else:
                                tree = phrase_fun.detect_phrase_components(
                                    parts[part_cnt], tree)
                                tree['what']['context'] = 'φράση'
                            logging.info(tree['what'])

                        else:
                            found_what, tree, is_plural = ActionTreeGenerator.get_nsubj_fallback(
                                tmp, tree, i)

                        # get content
                        if action not in [
                            'διαγράφεται',
                            'διαγράφονται',
                            'αναριθμείται',
                                'αναριθμούνται']:
                            tree, max_depth = ActionTreeGenerator.get_content(
                                tree, extract, s)

                        # split to subtrees
                        subtrees = ActionTreeGenerator.split_tree(tree)

                        # iterate over subtrees
                        for subtree in subtrees:

                            subtree, max_depth = ActionTreeGenerator.get_content(
                                subtree, extract, s, secondary=True)

                            # get latest statute
                            try:
                                law = ActionTreeGenerator.detect_latest_statute(
                                    non_extract)
                            except BaseException:
                                law = ''

                            # first level are laws
                            subtree['law'] = {
                                '_id': law,
                                'children': ['article']
                            }

                            splitted = non_extract.split(' ')

                            # build levels bottom up
                            subtree = ActionTreeGenerator.build_levels(
                                splitted, subtree)

                            # nest into dictionary
                            if nested:
                                ActionTreeGenerator.nest_tree('root', subtree)

                            trees.append(subtree)

        return trees

    @staticmethod
    def nest_tree_helper(vertex, tree):
        if tree[vertex] == {}:
            return tree
        if tree[vertex]['children'] == []:
            del tree[vertex]['children']
            return tree
        if len(tree[vertex]['children']) == 1:
            try:
                c = tree[vertex]['children'][0]
                del tree[vertex]['children']
                tree[vertex][c] = tree[c]
                ActionTreeGenerator.nest_tree(c, tree)
            except BaseException:
                return tree

    @staticmethod
    def nest_tree(vertex, tree):
        ActionTreeGenerator.nest_tree_helper(vertex, tree)

    @staticmethod
    def get_nsubj(doc, i, tree):
        found_what = False
        root_token = doc[i]
        for child in root_token.children:

            if child.dep_ in ['nsubj', 'obl']:
                for what in entities.whats:
                    if child.text == what:
                        found_what = True
                        tree['root']['children'].append('law')
                        tree['what'] = {
                            'index': child.i,
                            'context': what,
                        }
                        logging.info('nlp ok')

                        is_plural = helpers.is_plural(what)

                        return found_what, tree, is_plural

        return found_what, tree, False

    @staticmethod
    def get_nsubj_fallback(tmp, tree, i, max_what_window=20):
        found_what = False
        logging.info('Fallback mode')
        logging.info(tmp)
        for j in range(1, max_what_window + 1):
            for what in entities.whats:
                if i + j <= len(tmp) - 1 and what == tmp[i + j]:
                    tree['root']['children'].append('law')
                    tree['what'] = {
                        'index': i + j,
                        'context': what,
                    }

                    if i + j + 1 <= len(tmp):
                        tree['what']['number'] = list(
                            helpers.ssconj_doc_iterator(tmp, i + j))
                    else:
                        tree['what']['number'] = None

                    is_plural = helpers.is_plural(what)
                    return found_what, tree, is_plural

                if i - j >= 0 and what == tmp[i - j]:
                    tree['root']['children'].append('law')
                    tree['what'] = {
                        'index': i - j,
                        'context': what,
                    }
                    if i - j >= 0:
                        tree['what']['number'] = list(
                            helpers.ssconj_doc_iterator(tmp, i - j))
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
                x = idx + '. '
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
            end = spans[i + 1]
            result.append(q[start:end])

        return result

    @staticmethod
    def split_tree(tree):

        try:
            idx_list = tree['what']['number']
            extract = tree['what']['content']
            what = tree['what']['context']
        except BaseException:
            tree['what']['number'] = tree['what']['number'][0]
            return [tree]

        if len(idx_list) == 1:
            tree['what']['number'] = idx_list[0]
            result = [tree]

        else:
            result = []
            contents = ActionTreeGenerator.get_rois_from_extract(
                extract, what, idx_list)
            for idx, s in itertools.zip_longest(idx_list, contents):
                tmp = copy.deepcopy(tree)
                tmp['what']['number'] = idx
                tmp['what']['content'] = s
                result.append(tmp)

        return result

    @staticmethod
    def get_content(tree, extract, s, secondary=False):
        max_depth = 0
        if tree['what']['context'] in ['φράση', 'φράσεις', 'λέξη', 'λέξεις']:
            return tree, 6
        elif tree['what']['context'] in ['άρθρο', 'άρθρα']:
            if tree['root']['action'] != 'διαγράφεται':
                content = extract if not secondary else tree['what']['content']
                tree['article']['content'] = content
                tree['what']['content'] = content
            max_depth = 3

        elif tree['what']['context'] in ['παράγραφος', 'παράγραφοι']:
            if tree['root']['action'] != 'διαγράφεται':
                content = extract if not secondary else tree['what']['content']
                tree['paragraph']['content'] = content
                tree['what']['content'] = content
            max_depth = 4

        elif tree['what']['context'] in ['εδάφιο', 'εδάφια']:
            if tree['root']['action'] != 'διαγράφεται':
                content = extract if not secondary else tree['what']['content']
                tree['what']['content'] = content
            max_depth = 5

        elif tree['what']['context'] in ['περίπτωση', 'περιπτώσεις']:
            if tree['root']['action'] != 'διαγράφεται':
                content = extract
                tree['what']['content'] = content
            max_depth = 5

        elif tree['what']['context'] in ['υποπερίπτωση', 'υποπεριπτώσεις']:
            if tree['root']['action'] != 'διαγράφεται':
                content = extract
                tree['what']['content'] = content
            max_depth = 5

        return tree, max_depth

    @staticmethod
    def detect_with_iterator(non_extract_split, words):
        for i, w in enumerate(non_extract_split):
            if w in words:
                try:
                    iters = list(
                        helpers.ssconj_doc_iterator(
                            non_extract_split, i))
                    return iters[0]
                except BaseException:
                    continue

    @staticmethod
    def build_level(tmp, subtree, max_depth, stem):
        lookup = ActionTreeGenerator.trans_lookup[stem]

        if not re.search(stem, subtree['what']['context']):
            for i, w in enumerate(tmp):
                if re.search(stem, w):
                    subtree[lookup]['_id'] = next(
                        helpers.ssconj_doc_iterator(tmp, i))
                    subtree[lookup]['children'] = ActionTreeGenerator.children_loopkup[lookup]
                    break
        else:
            subtree[lookup]['_id'] = subtree['what']['number']
            subtree[lookup]['children'] = []

        return subtree

    @staticmethod
    def build_levels(tmp, subtree):
        stems = list(ActionTreeGenerator.trans_lookup.keys())
        for i, stem in enumerate(stems):
            subtree = ActionTreeGenerator.build_level(
                tmp, subtree, i + 2, stem)

        return subtree

    @staticmethod
    def phrase_analyze(s):
        s = tokenizer.tokenizer.remove_subordinate(s)
        parts = s.split(' ')
        phrase_regex = r'φράση «[^»]*»'

        tree = collections.defaultdict(dict)
        for i, p in enumerate(parts):
            for action in entities.actions:
                if action == p:
                    break

        for i, p in enumerate(parts):
            for what_stem in what_stems:
                if re.search(what_stem, p):
                    is_plural = helpers.is_plural(p)
                    it = helpers.ssconj_doc_iterator(
                        parts, i, is_plural=is_plural)
                    lookup = ActionTreeGenerator.trans_lookup[what_stem]
                    tree[lookup]['_id'] = next(it)

        for x in re.finditer(phrase_regex, s):
            print(helpers.get_extracts(x.group(), min_words=0))

        law = ActionTreeGenerator.detect_latest_statute(s)
