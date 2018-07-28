#!/usr/bin/env python3

import re
import sys
import syntax
import entities
import pparser as parser
import helpers
import database
import pprint
import tokenizer
import collections
import argparse
import multiprocessing
import gensim
from gensim.models import KeyedVectors
from networkx import (
    DiGraph,
    Graph,
    pagerank
)

class UnrecognizedCodificationAction(Exception):
    """Exception class which is raised when the
    codification action is not well-formed.
    """

    def __init__(self, extract):
        super().__init__('Unrecognized Codification Action on \n', extract)


class Link:
    """Link representation Class"""

    def __init__(self, name=''):
        """Initialize an Empty Link
        :param name : Name of link
        """

        self.is_sorted = 0
        self.name = name
        self.links_to = set([])
        self.actual_links = []

    def add_link(self, other, s, link_type='general'):
        """Add linking
        :params other : Neighbor
        :params s : Content
        :params link_type : Link type (can be modifying, referential etc.)
        """

        self.links_to |= {other}
        self.actual_links.append({
            'from': other,
            'text': s,
            'link_type': link_type,
            'status': 'μη εφαρμοσμένος'
        })

    def serialize(self):
        """Serialize link to dictionary"""

        return {
            '_id': self.name,
            'links_to': list(self.links_to),
            'actual_links': self.actual_links,
            'is_sorted' : self.is_sorted
        }

    def organize_by_text(self):
        """Format for rendering"""

        result = []

        for x in self.actual_links:
            text = x['text']
            tag = x['link_type']
            fr = x['from']
            status = x['status']
            q = (text, (tag, fr, status))
            result.append(q)

        return result

    def __dict__(self):
        """Serialize object"""

        return self.serialize()

    def __str__(self):
        """Return link name"""

        return self.name

    def __repr__(self):
        """Return link name"""

        return self.name

    def __iter__(self):
        """Yields actual_links elements"""

        for x in self.actual_links:
            yield x

    def __len__(self):
        """Returns number of edges"""

        return len(self.actual_links)

    def sort(self):
        """Sort actual links by year"""

        if self.is_sorted == 0:
            helpers.quicksort(self.actual_links, self.compare)
        self.is_sorted = 1

    def compare(self, x, y):
        """Comparator function by year, identifier and type
        params x, y: Items of self.actual_links
        """

        return helpers.compare_statutes(x['from'], y['from'])

    @staticmethod
    def from_serialized(s):
        """Create a link from a serialized object"""

        l = Link(s['_id'])
        l.links_to = set(s['links_to'])
        l.actual_links = s['actual_links']
        try:
            l.is_sorted = int(s['is_sorted'])
        except:
            l.is_sorted = 0
        return l


class LawCodifier:
    """This class is responsible for binding the different
    modules of the project into the codifier module.
    Functionality:
    1. Construct the database from Government Gazette issues
    2. Parsing New Laws and Fetching Last Versions from database
    3. Invoke Codification tool that recognizes actions and
    builds queries
    4. Interfacing with MongoDB
    """

    def __init__(self, issues_directory=None):
        """Constructor for LawCodifier class
        :param issues_directory : Issues directory
        """

        self.laws = {}
        self.links = {}
        self.topics = []
        self.db = database.Database()
        self.populate_laws()
        self.populate_links()
        self.populate_topics()
        self.issues = []
        if issues_directory:
            self.populate_issues(issues_directory)

        self.pagerank()

    def add_directory(self, issues_directory, text_format=True):
        """Add additional Directories"""

        self.issues.extend(
            parser.get_issues_from_dataset(
                issues_directory,
                text_format=text_format))

    def populate_topics(self):
        """Populate topics in codifier object"""

        cur = self.db.topics.find()
        for x in cur:
            self.topics.append(x)
        return self.topics

    def populate_laws(self):
        """Populate laws from database and fetch latest versions"""

        cursor = self.db.laws.find({"versions": {"$ne": None}})
        for x in cursor:

            current_version = 0
            current_instance = None
            for v in x['versions']:
                if int(v['_version']) >= current_version:
                    current_version = int(v['_version'])
                    current_instance = v

            law, identifier = parser.LawParser.from_serialized(v)
            law.version_index = current_version
            self.laws[identifier] = law

    def get_history(self, law):
        """Return the history and links of a certain law"""

        history = []

        cursor = self.db.laws.find({
            "_id": law,
            "versions": {"$ne": None}
        })
        for x in cursor:

            for v in x['versions']:
                current_version = int(v['_version'])
                current_instance = v
                instance, identifier = parser.LawParser.from_serialized(v)
                instance.version_index = current_version
                history.append(instance)

        try:
            history_links = sorted(self.links[law])
        except BaseException:
            history_links = {}

        return history, history_links

    def populate_issues(self, directory, text_format=True):
        """Populate issues from directory"""

        self.issues = parser.get_issues_from_dataset(
            directory, text_format=text_format)

    def codify_issue(self, filename):
        """Codify certain issue (legacy)
        :params filename : Issue filename
        """

        trees = {}
        issue = parser.IssueParser(filename)
        sorted_articles = sorted(issue.articles.keys())

        for article in sorted_articles:

            for i, extract in enumerate(issue.get_non_extracts(article)):
                trees[i] = syntax.ActionTreeGenerator.generate_action_tree(
                    extract, issue, article)
                for j, t in enumerate(trees[i]):
                    print(t['root'])
                    print(t['what'])
                    law_id = t['law']['_id']
                    print('Law id is ', law_id)

                    try:

                        if law_id not in self.laws.keys():
                            print('Not in keys')
                            self.laws[law_id] = parser.LawParser(law_id)

                        self.db.query_from_tree(self.laws[law_id], t)

                        print('Pushed to Database')
                    except Exception as e:
                        print(str(e))
                        continue

                    print('\nPress any key to continue')
                    input()

    def codify_law(self, identifier):
        """
        Codify certain law. Search all issues within self.issues
        :param identifier : The law identifier e.g. ν. 1234/5678
        """
        trees = {}

        for issue in self.issues:
            for article in issue.find_statute(identifier):
                print(article, issue.name)
                print('Codifying')

                for i, non_extract in enumerate(
                        issue.get_non_extracts(article)):
                    trees[i] = syntax.ActionTreeGenerator.generate_action_tree(
                        non_extract, issue, article)
                    for j, t in enumerate(trees[i]):
                        print(t['root'])
                        print(t['what'])
                        law_id = t['law']['_id']
                        print('Law id is ', law_id)

                        try:

                            if law_id not in self.laws.keys():
                                print('Not in keys')
                                self.laws[law_id] = parser.LawParser(law_id)

                            print('Ammendee, ', issue.name)
                            self.db.query_from_tree(
                                self.laws[law_id], t, issue.name)

                            print('Pushed to Database')
                        except Exception as e:
                            print(str(e))
                            continue

                        print('\nPress any key to continue')
                        input()

    def codify_new_laws(self):
        """Append new laws found in self.issues"""

        for issue in self.issues:
            new_laws = issue.detect_new_laws()
            print(new_laws)
            for k in new_laws.keys():
                try:
                    serializable = new_laws[k].__dict__()
                    serializable['_version'] = 0
                    serializable['amendee'] = k
                    try:
                        serializable['issue'] = helpers.parse_filename(issue.filename)
                    except:
                        pass
                    self.db.laws.save({
                        '_id': new_laws[k].identifier,
                        'versions': [
                            serializable
                        ]
                    })
                except BaseException:
                    pass

    def get_law(self, identifier, export_type='latex'):
        """Get law string in LaTeX, Markdown, str, plaintext or issue-like format
        :param identifier : Law identifier
        """
        result = self.laws[identifier].export_law(export_type=export_type)
        return result

    def export_codifier_corpus(self, outfile, labels=None):
        """Export every law in a line in str format"""
        if labels:
            labels = open(labels, 'w+')
        with open(outfile, 'w+') as f:
            for law in self.laws:
                s = self.get_law(law, export_type='str')
                f.write(s + '\n')
                labels.write(str(law) + '\n')
        labels.close()

    def export_phrase_links(self, outfile):
        """Export links that have to do with operations
        on phrases in plaintext format"""
        with open(outfile, 'w+') as f:
            for l, lobj in self.links.items():
                for x in lobj:
                    periods = tokenizer.tokenizer.split(
                        x['text'], False, '. ')
                    for p in periods:
                        if re.search(r'(φράση|φράσεις)', p):
                            f.write(p + '\n')

    def export_law(self, identifier, outfile, export_type='markdown'):
        """Export a law in markdown or LaTeX"""

        if export_type not in ['latex', 'markdown', 'str', 'plaintext', 'issue']:
            raise Exception('Unrecognized export type')

        result = self.get_law(identifier, export_type=export_type)
        if export_type == 'latex':
            helpers.texify(result, outfile)
        elif export_type == 'markdown':
            with open(outfile, 'w+') as f:
                f.write(result)

    def create_law_links(self):
        """Creates links from existing laws"""

        for identifier, law in self.laws.items():
            articles = law.sentences.keys()

            for article in articles:
                for paragraph in law.get_paragraphs(article):
                    try:
                        extracts, non_extracts = helpers.get_extracts(
                            paragraph, 0)

                        for entity in entities.LegalEntities.entities:
                            # If law found in amendment body then it is
                            # modifying
                            for s in non_extracts:

                                neighbors = re.finditer(entity, s)
                                neighbors = set([neighbor.group()
                                                 for neighbor in neighbors])

                                tmp = s.split(' ')

                                for u in neighbors:
                                    if u not in self.links:
                                        self.links[u] = Link(u)
                                    is_modifying = False

                                    for action in entities.actions:
                                        for i, w in enumerate(tmp):
                                            if action == w:
                                                is_modifying = True
                                                break
                                        if is_modifying:
                                            break

                                    if is_modifying:
                                        self.links[u].add_link(
                                            law.identifier, paragraph, link_type='τροποποιητικός')
                                    else:
                                        self.links[u].add_link(
                                            law.identifier, paragraph, link_type='αναφορικός')

                            # If enclosed in brackets the link is only
                            # referential
                            for s in extracts:
                                neighbors = re.finditer(entity, s)
                                neighbors = set([neighbor.group()
                                                 for neighbor in neighbors])

                                for u in neighbors:
                                    u = u.lower()
                                    if u not in self.links:
                                        self.links[u] = Link(u)

                                    self.links[u].add_link(
                                        law.identifier, paragraph, link_type='αναφορικός')
                    # except there are Unmatched brackets
                    except Exception as e:
                        neighbors = re.finditer(entity, paragraph)
                        neighbors = set([neighbor.group()
                                         for neighbor in neighbors])

                        for u in neighbors:

                            if u not in self.links:
                                self.links[u] = Link(u)

                            self.links[u].add_link(
                                law.identifier, paragraph, link_type='γενικός')

        for link in self.links.values():
            self.db.links.save(link.serialize())

    def populate_links(self):
        """Populate links from database and fetch latest versions"""

        cursor = self.db.links.find()

        for x in cursor:
            l = Link.from_serialized(x)
            self.links[str(l)] = l

    def keys(self):
        """Return set of keys for the codifier"""
        return list(set(self.laws.keys()) | set(self.links.keys()))

    def topic_keys(self):
        """Return topic keywords in a set"""
        topic_k = set([])
        for topic in self.topics:
            topic_k |= set(topic['keywords'])
        return list(topic_k)

    def calculate_links_degrees(self):
        """Calculate statistics of links"""
        cursor = self.db.links.find({})
        max_degree = -1
        sum_degrees = 0
        cnt = 0

        for x in cursor:
            d = len(set(x['links_to']))
            max_degree = max(max_degree, d)
            sum_degrees += d
            cnt += 1

        avg_degree = sum_degrees / cnt
        print('Maximum Degree: ', max_degree)
        print('Average Degree', avg_degree)

    def train_word2vec(self):
        """Train a word2vec model using the words of the codifier"""
        params = {
            'size': 200,
            'iter': 20,
            'window': 2,
            'min_count': 15,
            'workers': max(
                1,
                multiprocessing.cpu_count() -
                1),
            'sample': 1E-3,
        }

        all_sentences = []

        for law in self.laws.values():
            for article in law.sentences.keys():
                for par in law.sentences[article]:
                    for per in law.sentences[article][par]:
                        all_sentences.append(per)

        self.model = gensim.models.Word2Vec(all_sentences, **params)
        print('Model train complete!')
        self.model.wv.save_word2vec_format('model')

        return self.model

    def build_graph_from_links(self, link_type=None):
        """Build nx.Graph from links of a certain type
        :params link_type : The link type (e.g. αναφορικός) for
        building the graph (default is None to use all links)"""
        edges = []
        for u, link in self.links.items():
            for v in link:
                if not link_type or (link_type and v['link_type'] == link_type):
                    edge = (u, v['from'])
                    edges.append(edge)

        self.graph = Graph()
        self.graph.add_edges_from(edges)
        return self.graph

    def pagerank(self):
        """Run pagerank on graph built from links"""
        self.graph = self.build_graph_from_links()
        self.ranks = pagerank(self.graph, alpha=0.9)
        return self.ranks

def build(start=1998, end=2018, data_dir='../data/', pipeline=['laws', 'links', 'topics', 'versions'], drop=True):
    """Build codifier object
    :params start : Start year
    :params end : End year
    :params data_dir : Text files directory
    :params pipeline : Pipeline to build
    Full pipeline ['laws', 'links', 'topics', 'versions']
    laws: Build laws
    links: Build links
    topics: Build topics
    versions: Build versions
    """
    # Import here for performance
    import topic_models
    import apply_links

    # Create object to be returned
    cod = LawCodifier()

    # Add build dirs
    if 'laws' in pipeline:
        for i in range(start, end + 1):
            cod.add_directory(data_dir + str(i))

    # Build Lookup
    build_lookup = {
        'laws' : cod.codify_new_laws,
        'links' : cod.create_law_links,
        'topics' : topic_models.build_topics,
        'versions' : apply_links.apply_all_links
    }

    # Drop Lookup
    drop_lookup = {
        'laws' : cod.db.drop_laws,
        'links' : cod.db.drop_links,
        'topics' : cod.db.drop_topics,
        'versions' : cod.db.rollback_all
    }

    # Apply stages
    for stage in pipeline:
        print('Building {}'.format(stage))
        if drop:
            drop_lookup[stage]()
        build_lookup[stage]()

    return cod

# Codifier object
codifier = LawCodifier()
