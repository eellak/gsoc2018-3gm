#!/usr/bin/env python3
import tokenizer
import copy
import re
import multiprocessing
import numpy as np
from datetime import date, datetime, time
import collections
import helpers
import entities
import string
import os
import gensim
import mimetypes
import logging
import pprint
from gensim.models import KeyedVectors
import logging
import itertools
import glob
import sys
import phrase_fun
import syntax
import json

# configuration and parameters

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

params = {'size': 200, 'iter': 20, 'window': 2, 'min_count': 15,
          'workers': max(1, multiprocessing.cpu_count() - 1), 'sample': 1E-3, }

date_regex = re.compile('(\
([1-9]|0[1-9]|[12][0-9]|3[01])\
[-/.\s+]\
(1[1-2]|0[1-9]|[1-9]|Ιανουαρίου|Φεβρουαρίου|Μαρτίου|Απριλίου|Μαΐου|Ιουνίου|Ιουλίου|Αυγούστου|Νοεμβρίου|Δεκεμβρίου|Σεπτεμβρίου|Οκτωβρίου|Ιαν|Φεβ|Μαρ|Απρ|Μαϊ|Ιουν|Ιουλ|Αυγ|Σεπτ|Οκτ|Νοε|Δεκ)\
(?:[-/.\s+](1[0-9]\d\d|20[0-9][0-8]))?)')


class IssueParser:
    """
    This is a class for holding information about an issue in
    computer-friendly form. It is responsible for:
    1. Detecting Dates
    2. Split document to articles
    3. Split articles to extracts and non-extracts for assisting
    in construction of the parse tree for each ROI.
    4. Detect Signatories of Given Documents
    5. Train a word2vec model with gensim for further usage."""

    def __init__(self, filename, stdin=False, toTxt=False):
        self.filename = filename
        self.lines = []
        tmp_lines = []

        if not stdin:
            filetype = mimetypes.guess_type(filename)[0]

            # if it is in PDF format convert it to txt
            if filetype == 'application/pdf':
                outfile = filename.replace('.pdf', '.txt')
                if not os.path.isfile(outfile):
                    os.system('pdf2txt.py {} > {}'.format(filename, outfile))
                filename = outfile
            elif filetype != 'text/plain':
                raise UnrecognizedFileException(filename)

        if not stdin:
            infile = open(filename, 'r')

        # remove ugly hyphenthation
        while True:
            if not stdin:
                l = infile.readline()
            else:
                l = sys.stdin.readline()
            if not l:
                break
            l = l.replace('−\n', '')
            l = l.replace('\n', ' ')
            l = re.sub(r' +', ' ', l)
            l = helpers.fix_par_abbrev(l)
            tmp_lines.append(l)

        if not stdin:
            infile.close()

        for line in tmp_lines:
            if line == '':
                continue
            elif line.startswith('Τεύχος') or line.startswith('ΕΦΗΜΕΡΙ∆Α TΗΣ ΚΥΒΕΡΝΗΣΕΩΣ') or line.startswith('ΕΦΗΜΕΡΙΣ ΤΗΣ ΚΥΒΕΡΝΗΣΕΩΣ'):
                continue
            else:
                try:
                    n = int(line)
                    continue
                except ValueError:
                    self.lines.append(line)
                    if line.startswith('Αρ. Φύλλου'):
                        for x in line.split(' '):
                            if x.isdigit():
                                self.issue_number = x
                                break

        self.dates = []
        self.find_dates()
        self.articles = {}
        self.articles_as_paragraphs = {}
        if not stdin:
            self.name = filename.replace('.pdf', '')
        else:
            self.name = 'stdin'
        self.sentences = {}
        self.find_articles()
        self.detect_statutes()

    def __str__(self):
        return self.name

    def split_article(self, article):
        paragraphs = collections.defaultdict(list)

        paragraph_ids = [
            par_id.group().strip('.') for par_id in re.finditer(
                r'\d+.', self.articles[article])]
        paragraph_corpus = list(
            filter(
                lambda x: x.rstrip() != '',
                re.split(
                    r'\d+.',
                    self.articles[article])))
        paragraph_corpus = [p.rstrip().lstrip() for p in paragraph_corpus]
        return paragraph_corpus

    def detect_statutes(self):
        """Detect all statutes within the issue
        such as Laws, Decrees and Acts"""

        self.statutes = {}

        for article in self.articles.keys():
            for extract in self.get_non_extracts(article):

                legislative_acts = list(re.finditer(
                    entities.legislative_act_regex, extract))
                laws = list(re.finditer(entities.law_regex, extract))
                presidential_decrees = list(re.finditer(
                    entities.presidential_decree_regex, extract))
                legislative_decrees = list(re.finditer(
                    entities.legislative_decree_regex, extract))

                self.statutes[article] = []
                self.statutes[article].extend(laws)
                self.statutes[article].extend(legislative_acts)
                self.statutes[article].extend(presidential_decrees)
                self.statutes[article].extend(legislative_decrees)

                self.statutes[article] = [statute.group()
                                          for statute in self.statutes[article]]

        return self.statutes

    def __contains__(self, key):
        for article in self.articles.keys():
            if key in self.statutes[article]:
                return True
        return False

    def find_statute(self, key):
        for article in sorted(self.articles.keys()):
            if key in self.statutes[article]:
                yield article

    def serialize(self):
        serializable = {
            '_id': self.__str__(),
            'date': str(self.issue_date),
            'articles': self.articles,
            'articles_as_paragraphs': self.articles_as_paragraphs,
            'dates': self.dates,
            'statutes': self.statutes,
            'extracts': self.extracts
        }
        return serializable

    def __dict__(self):
        return self.serialize()

    def find_dates(self):
        """Detect all dates withing the given document"""
        year_regex = r'([1-2][0-9][0-9][0-9])'
        now = datetime.now()

        for i, line in enumerate(self.lines):
            result = date_regex.findall(line)
            if result != []:
                self.dates.append((i, result))

        for line in self.lines:
            res = re.search(year_regex, line)
            if res:
                result = int(res.group())
                if 1976 <= result <= now.year:
                    self.year = result
                    break

        if self.dates == []:
            logging.warning('Could not find dates!')
            return []
        try:
            self.issue_date = string_to_date(self.dates[0][1][0])
            self.signed_date = self.dates[-1]
        except IndexError:
            logging.warning('Could not find dates!')
        finally:
            return self.dates

    def parse_name(self):
        # parse 20150100022.txt
        r = helpers.split_index(s, [4, 6, 8])
        return 'ΦΕΚ Α {}/{}'.format(r[-1], r[1])

    def find_articles(self, min_extract_chars=100):
        """Split the document into articles,
        Detect Extracts that are more than min_extract_chars.
        Extracts start with quotation marks	(«, »).
        Strip punctuation and split document into sentences.
        """

        article_indices = []
        for i, line in enumerate(self.lines):
            if line.startswith('Άρθρο') or line.startswith(
                    'Ο Πρόεδρος της Δημοκρατίας'):
                article_indices.append((i, line))
                self.articles[line] = ''

        for j in range(len(article_indices) - 1):

            content = self.lines[article_indices[j]
                                 [0] + 1: article_indices[j + 1][0]]
            paragraphs = collections.defaultdict(list)
            current = '0'
            for t in content:
                x = re.search(r'\d+.', t)
                if x and x.span() in [(0, 2), (0, 3)]:
                    current = x.group().strip('.')
                paragraphs[current].append(t)

            sentences = {}

            for par in paragraphs.keys():
                val = ''.join(paragraphs[par])[1:]
                paragraphs[par] = val
                sentences[par] = list(
                    filter(
                        lambda x: x.rstrip() != '',
                        tokenizer.tokenizer.split(val, False, '. ')))

            self.articles[article_indices[j][1]] = ''.join(content)
            self.articles_as_paragraphs[article_indices[j][1]] = paragraphs
        try:
            del self.articles['Ο Πρόεδρος της Δημοκρατίας']
        except BaseException:
            pass

        self.extracts = {}
        self.non_extracts = {}

        for article in self.articles.keys():

            # find extracts
            left_quot = [m.start()
                         for m in re.finditer('«', self.articles[article])]
            right_quot = [m.start()
                          for m in re.finditer('»', self.articles[article])]
            left_quot.extend(right_quot)
            temp_extr = sorted(left_quot)
            res_extr = []
            c = '«'
            for idx in temp_extr:
                if c == '«' and self.articles[article][idx] == c:
                    res_extr.append(idx)
                    c = '»'
                elif c == '»' and self.articles[article][idx] == c:
                    res_extr.append(idx)
                    c = '«'
            self.extracts[article] = list(zip(res_extr[::2], res_extr[1::2]))

            # drop extracts with small chars
            self.extracts[article] = sorted(
                list(
                    filter(
                        lambda x: x[1] -
                        x[0] +
                        1 >= min_extract_chars,
                        self.extracts[article])),
                key=lambda x: x[0])

            tmp = self.articles[article].strip('-').split('.')

            # remove punctuation
            tmp = [re.sub(r'[^\w\s]', '', s) for s in tmp]
            tmp = [line.split(' ') for line in tmp]
            self.sentences[article] = tmp

    def get_extracts(self, article):
        """Get direct parts that should be added, modified or deleted"""
        for i, j in self.extracts[article]:
            yield self.articles[article][i + 1: j]

    def get_non_extracts(self, article):
        """Get non-extracts i.e. where the commands for ammendments
        can be found"""

        if len(self.extracts[article]) == 0:
            yield self.articles[article]
            return
        x0, y0 = self.extracts[article][0]
        yield self.articles[article][0: max(0, x0)]

        for i in range(1, len(self.extracts[article]) - 1):
            x1, y1 = self.extracts[article][i]
            x2, y2 = self.extracts[article][i + 1]
            yield self.articles[article][y1 + 1: x2]
        xl, yl = self.extracts[article][-1]

        yield self.articles[article][yl + 1:]

    def get_alternating(self, article):
        """Get extracts and non-extracts alternating as a generator"""

        # start with an extract
        if self.extracts[article][0] == 0:
            flag = False
        else:
            flag = True

        extracts_ = list(self.get_extracts(article))
        non_extracts_ = list(self.get_non_extracts(article))

        for e, n in itertools.zip_longest(extracts_, non_extracts_):
            if flag:
                if n is not None:
                    yield n
                if e is not None:
                    yield e
            else:
                if e is not None:
                    yield e
                if n is not None:
                    yield n

    def all_sentences(self):
        for article in self.sentences.keys():
            for sentence in self.sentences[article]:
                yield sentence

    def detect_signatories(self):
        self.signatories = set([])
        for i, line in enumerate(self.lines):
            if line.startswith('Ο Πρόεδρος της Δημοκρατίας'):
                minister_section = self.lines[i:]
                break

        for i, line in enumerate(minister_section):
            for minister in ministers:
                x = minister.is_mentioned(line)
                if x is not None:
                    self.signatories |= set([minister])

        for signatory in self.signatories:
            logging.info(signatory)

        self.signatories = list(self.signatories)

        return self.signatories

    def detect_new_laws(self):
        """Detect new laws being added to Greek
        Legislation. Proceedure includes
        1. Detection of regular expressions that undermine new addition
        2. Detection of the new law identifier
        3. Construction of LawParser Objects and parse the law corpus
        4. Keep the new laws in a dictionary"""

        new_law_regex = entities.LegalEntities.ratification
        self.new_laws = {}
        regions_of_interest = []

        for i, line in enumerate(self.lines):
            if re.search(new_law_regex, line):
                regions_of_interest.append(i)

        if regions_of_interest == []:
            return self.new_laws
        else:
            regions_of_interest.append(len(self.lines) - 1)

        for start, end in zip(regions_of_interest, regions_of_interest[1:]):

            for j, line in enumerate(self.lines[start:end]):
                i = j + start
                result = re.search(new_law_regex, line + self.lines[i + 1])
                if result:
                    result = result.group().rstrip().split(' ')

                    abbreviation = 'ν.'

                    if result[0] == 'ΠΡΟΕΔΡΙΚΟ':
                        abbreviation = 'π.δ.'
                    elif result[0] == 'ΚΟΙΝΗ':
                        abbreviation = 'ΚΥΑ'
                    elif result[0] == 'ΝΟΜΟΘΕΤΙΚΟ':
                        abbreviation = 'ν.δ.'

                    identifier = '{} {}/{}'.format(abbreviation,
                                                   result[-1], self.year)
                    logging.info(
                        'Issue: ' +
                        self.name +
                        'Identifier: ' +
                        identifier)

                    ignore = True

                    self.new_laws[identifier] = LawParser(identifier)
                    self.new_laws[identifier].lines = self.lines
                    self.new_laws[identifier].find_corpus(
                        government_gazette_issue=True)

        return self.new_laws


class UnrecognizedFileException(Exception):

    def __init__(self, filename):
        super().__init__('Unrecognized filetype ' + str(filename))


def get_issues_from_dataset(directory='../data', text_format=False):
    cwd = os.getcwd()
    os.chdir(directory)
    issues = []
    if text_format:
        filelist = glob.glob('*.txt')
        for filename in filelist:
            issue = IssueParser(filename)
            issues.append(issue)
    else:
        filelist = glob.glob('*.pdf')
        for filename in filelist:
            outfile = filename.strip('.pdf') + '.txt'
            logging.info(outfile)
            if not os.path.isfile(outfile):
                os.system('pdf2txt.py {} > {}'.format(filename, outfile))
            issue = IssueParser(outfile)
            issues.append(issue)

    os.chdir(cwd)
    return issues


class LawParser:
    """
    This class hosts the law parser. The law is provided
    in a file (if it exists) and is parsed in order to be
    split in articles and sentences, ready to be stored in
    the database. This class supports insertions, replacements
    and deletions of articles, paragraphs, phrases and periods.
    It can also provide a serializable object for updating the
    database with its contents.
    """

    def __init__(self, identifier, filename=None, autoincrement_version=False):
        """The constructor of LawParser is responsible for
        reading and parsing the file as well as detecting
        titles, lemmas and articles which are split into sentences
        by find_corpus()

        :param identifier This is the law identifier (for example ν. 1920/1991)
        :param filename (optional) the text file
        """
        self.lines = []
        self.identifier = identifier
        self.autoincrement_version = autoincrement_version
        self.version_index = 0
        if filename and isinstance(filename, str):
            self.filename = filename
            tmp_lines = []
            with open(filename, 'r') as infile:
                # remove ugly hyphenthation
                while 1 == 1:
                    l = infile.readline()
                    if not l:
                        break
                    l = l.replace('-\n', '')
                    l = l.replace('\n', ' ')
                    tmp_lines.append(l)

            for line in tmp_lines:
                if line == '':
                    continue
                else:
                    self.lines.append(line)
        self.thesaurus = {}
        self.lemmas = {}
        self.articles = collections.defaultdict(dict)
        self.titles = {}
        self.corpus = {}
        self.sentences = collections.defaultdict(dict)
        self.amendee = None

        self.find_corpus(fix_paragraphs=False)

    def __repr__(self):
        return self.identifier

    def __str__(self):
        return self.identifier

    def fix_paragraphs(self, lines, get_title=True):
        """Fix paragraphs in a text. That means that
        a corpus of lines enumerated with natural numbers
        1., 2., etc. would be groupped into respective
        paragraps
        """
        result = []

        if lines[0].startswith('Άρθρο'):
            lines.pop()

        indices = []
        start = 0

        for i, t in enumerate(lines):
            x = re.search(r'\d+.', t)
            if x and x.span() in [(0, 2), (0, 3)]:
                try:
                    number = int(x.group().split('.')[0])
                except BaseException:
                    continue
                if number == start + 1:
                    indices.append(i)
                    start += 1

        for j in range(len(indices) - 1):

            content = lines[indices[j]: indices[j + 1]]
            result.append(content)

        if result != []:
            result.append(lines[indices[-1]:])
            result = [''.join(r) for r in result]

            if get_title:
                title = ''.join(lines[:indices[0]])
            else:
                title = None

            return result, title
        else:
            splitter = -1
            for i, line in enumerate(lines):
                if line.rstrip() == '':
                    splitter = i
                    break

            # Split in first ' ' character
            # The article title is before the space character(s)
            # The rest is after the space character(s)
            if splitter != -1:
                title = ''.join(lines[:splitter])
                result = '1. ' + ''.join(lines[splitter:])
            else:
                result = ''.join(lines)
                title = ''
            return result, title

    def fix_name(self, name):
        if name.isdigit():
            return name
        else:
            try:
                return str(entities.Numerals.full_number_to_integer(name))
            except BaseException:
                return name

    def find_corpus(self, government_gazette_issue=False, fix_paragraphs=True):
        """Analyzes the corpus to articles, paragraphs and
        then sentences"""

        idx = []
        for i, line in enumerate(self.lines):
            if line.startswith('Αρθρο:') or line.startswith('Άρθρο '):
                idx.append(i)

        for j in range(len(idx) - 1):
            x, y = idx[j], idx[j + 1]
            self.lines[x] = self.lines[x].strip(':').replace(':\t', ' ')
            name = self.lines[x].rstrip().replace(
                'Αρθρο: ', '').replace('Άρθρο ', '')
            name = self.fix_name(name)
            self.corpus[name] = self.lines[x: y]

        if fix_paragraphs:

            for Κείμενοarticle in self.corpus.keys():
                fixed_lines, title = self.fix_paragraphs(self.corpus[article])
                self.titles[article] = title
                self.corpus[article] = fixed_lines
                self.prune_title(article)

        for article in self.corpus.keys():
            for i, line in enumerate(self.corpus[article]):
                if line.startswith(
                        'Κείμενο Αρθρου') or government_gazette_issue:
                    if government_gazette_issue:
                        self.articles[article] = self.corpus[article]
                    elif line.startswith('Κείμενο Άρθρου'):

                        self.articles[article] = self.corpus[article][i + 1:]
                    paragraphs = collections.defaultdict(list)
                    current = '0'
                    for t in self.articles[article]:
                        x = re.search(r'\d+.', t)
                        if x and x.span() in [(0, 2), (0, 3)]:
                            current = x.group().strip('.')
                        paragraphs[current].append(t)

                    sentences = {}

                    for par in paragraphs.keys():
                        val = ''.join(paragraphs[par])[1:]
                        val = helpers.fix_whitespaces(val)
                        val = helpers.fix_par_abbrev(val)
                        val = helpers.fix_hyphenthation(val)
                        paragraphs[par] = val
                        sentences[par] = list(
                            filter(
                                lambda x: x.rstrip() != '',
                                tokenizer.tokenizer.split(
                                    val, False, '. ')
                            )
                        )

                    self.articles[article] = paragraphs
                    self.sentences[article] = sentences

                    if government_gazette_issue:
                        break

    def __dict__(self):
        return self.serialize()

    def serialize(self):
        """Returns the object in database-friendly format
        in a dictionary.
        """
        if self.autoincrement_version:
            self.version_index += 1

        return {
            '_id': self.identifier,
            'thesaurus': self.thesaurus,
            'lemmas': self.lemmas,
            'titles': self.titles,
            'articles': self.sentences,
            'amendee': self.amendee
        }

    @staticmethod
    def from_serialized(x):
        identifier = x['_id']
        law = LawParser(identifier)
        law.thesaurus = x['thesaurus']
        law.lemmas = x['lemmas']
        law.titles = x['titles']
        law.sentences = x['articles']
        law.amendee = x['amendee']
        try:
            law.issue = x['issue']
        except BaseException:
            law.issue = ''

        return law, identifier

    def add_article(self, article, content, title=None, lemmas=None):
        """Add article from content
        :param article the article id
        :param content the content in raw text
        :title (optional) title of article
        :lemmas (optional) lemmas for article
        """
        # prepare context
        article = str(article)
        paragraphs = collections.defaultdict(list)

        paragraph_ids = [par_id.group().strip('.')
                         for par_id in re.finditer(r'\d+.', content)]

        # filter ids
        filtered_ids = []
        current = 1
        for i, x in enumerate(paragraph_ids):
            if int(x) == current:
                filtered_ids.append(x + '.')
                current += 1

        if len(paragraph_ids) == 0:
            filtered_ids = ['1']

        filtered_ids_regex = '|'.join(map(re.escape, filtered_ids))
        paragraph_corpus = list(
            filter(
                lambda x: x.rstrip() != '',
                re.split(
                    filtered_ids_regex,
                    content)))
        paragraph_corpus = [p.rstrip().lstrip() for p in paragraph_corpus]
        sentences = {}
        paragraphs = {}
        for kkey, val in itertools.zip_longest(filtered_ids, paragraph_corpus):
            if kkey is None or val is None:
                break
            key = kkey.strip('. ')
            sentences[key] = tokenizer.tokenizer.split(val, False, '. ')
            paragraphs[key] = val

        self.sentences[article] = sentences

        if title:
            self.titles[article] = title
        if lemmas:
            self.lemmas[article] = lemmas

        return self.serialize()

    def remove_article(self, article):
        """Removal of article based on its id
        :param artitcle id
        """

        article = str(article)
        try:
            del self.sentences[article]
        except BaseException:
            logging.warning('Could not find sentences')
        try:
            del self.corpus[article]
        except BaseException:
            logging.warning('Could not find corpus')
        try:
            del self.lemmas[article]
        except BaseException:
            logging.warning('Could not find lemmas')
        try:
            del self.titles[article]
        except BaseException:
            logging.warning('Could not find titles')

        return self.serialize()

    def add_paragraph(self, article, paragraph, content):
        """Addition of paragraph on article
        :article article id
        :paragraph paragraph id
        :content content in raw text to be split into periods
        """

        article = str(article)
        paragraph = str(paragraph)

        # prepare content for modification
        try:
            content = helpers.remove_front_num(content).rstrip('.')
        except BaseException:
            content = content.rstrip('.')

        # add in its full form or split into periods
        self.articles[article][paragraph] = content
        self.sentences[article][paragraph] = tokenizer.tokenizer.split(
            content, False, '. ')

        return self.serialize()

    def remove_paragraph(self, article, paragraph):
        """Removal of paragraph"""

        article = str(article)
        paragraph = str(paragraph)

        try:
            del self.sentences[article][paragraph]
        except BaseException:
            pass

        return self.serialize()

    def replace_phrase(
            self,
            old_phrase,
            new_phrase,
            article=None,
            paragraph=None):
        """Replacement of phrase inside document
        :old_phrase phrase to be replaced
        :new_phrase new phrase
        :article optional detect phrase in certain article
        :paragraph optional detect phrase in certain paragraph
        """
        self.sentences[article][paragraph] = phrase_fun.replace_phrase(
            self.sentences[article][paragraph],
            new_phrase=new_phrase,
            old_phrase=old_phrase
        )

        return self.serialize()

    def remove_phrase(self, old_phrase, article=None, paragraph=None):
        """Removal of certain phrase i.e. replacement with empty string"""

        return self.replace_phrase(old_phrase, '', article, paragraph)

    def insert_phrase(
            self,
            new_phrase,
            position='append',
            old_phrase='',
            article=None,
            paragraph=None):
        """Phrase insertion with respect to another phrase"""

        self.sentences[article][paragraph] = phrase_fun.insert_phrase(
            self.sentences[article][paragraph],
            new_phrase=new_phrase,
            position=position,
            old_phrase=old_phrase
        )

        return self.serialize()

    def renumber_case(
            self,
            case_letter,
            new_letter,
            article,
            paragraph,
            suffix=')'):
        """Renumbering of a case in a paragraph
        :params case_letter : Old case letter
        :params new_letter : New case letter
        :params article : Article Number
        :params paragraph : Paragraph Number
        """

        self.sentence[article][paragraph] = phrase_fun.renumber_case(
            s=self.sentences[article][paragraph],
            case_letter=case_letter,
            new_letter=new_letter,
            suffix=suffix)

        return self.serialize()

    def insert_case(
            self,
            case_letter,
            content,
            article,
            paragraph,
            suffix=')'):
        """Insertion of a case (of arbitrary depth) in the document
        params case_letter: The greek case letter
        params content : Content to be inserted
        params suffix : ending suffix
        params article : article number
        params paragraph : paragraph number
        """

        tmp = phrase_fun.insert_case(
            s=self.sentences[article][paragraph],
            case_letter=case_letter,
            content=content,
            suffix=suffix
        )

        return self.serialize()

    def replace_case(
            self,
            case_letter,
            new_content,
            article,
            paragraph,
            suffix=')'):
        """Replacement of a case (of arbitrary depth) in the document
        params case_letter: The greek case letter
        params content : Content to be inserted
        params suffix : ending suffix
        params article : article number
        params paragraph : paragraph number
        """

        self.sentences[article][paragraph] = phrase_fun.replace_case(
            s=self.sentences[article][paragraph],
            case_letter=case_letter,
            new_content=new_content,
            suffix=suffix
        )

        return self.serialize()

    def delete_case(
            self,
            case_letter,
            article,
            paragraph):
        """Deletion of a case (of arbitrary depth) in the document
        params case_letter: The greek case letter
        params content : Content to be inserted
        params suffix : ending suffix
        params article : article number
        params paragraph : paragraph number
        """

        self.sentences[article][paragraph] = phrase_fun.delete_case(
            s=self.sentences[article][paragraph],
            case_letter=case_letter,
        )

        return self.serialize()

    def replace_period(
            self,
            old_period,
            new_period,
            position=None,
            article=None,
            paragraph=None):
        """Replacement of a period with new content"""
        if position is None:
            search_all = (article is None)

            if article:
                delegate_articles = [str(article)]

                if paragraph:
                    delegate_paragraphs = [str(paragraph)]
                else:
                    delegate_paragraphs = self.sentences[article].keys()
            else:
                delegate_articles = self.articles.keys()

            for article in delegate_articles:
                if search_all:
                    delegate_paragraphs = self.sentences[article].keys()

                for paragraph in delegate_paragraphs:
                    for i, period in enumerate(
                            self.sentences[article][paragraph]):
                        if old_period == period:
                            self.sentences[article][paragraph][i] = new_period
        elif position == 'append':
            self.sentences[article][paragraph][-1] = new_period
        else:
            self.sentences[article][paragraph][int(position)] = new_period

        return self.serialize()

    def remove_period(
            self,
            old_period,
            position=None,
            article=None,
            paragraph=None):
        """Removal of period"""

        search_all = (article is None)

        if position is None:
            if article:
                delegate_articles = [str(article)]

                if paragraph:
                    delegate_paragraphs = [str(paragraph)]
                else:
                    delegate_paragraphs = self.sentences[article].keys()
            else:
                delegate_articles = self.sentences.keys()

            for article in delegate_articles:
                if search_all:
                    delegate_paragraphs = self.sentences[article].keys()

                for paragraph in delegate_paragraphs:
                    for i, period in enumerate(
                            self.sentences[article][paragraph]):
                        if old_period == period or old_period == period[:-1]:
                            del self.sentences[article][paragraph][i]
                            return self.serialize()
        else:
            del self.sentences[article][paragraph][int(position)]

        return self.serialize()

    def insert_period(
            self,
            position,
            old_period,
            new_period,
            article=None,
            paragraph=None):
        """Insertion of period relative to another period"""

        assert(
            position in [
                'start',
                'end',
                'before',
                'after'] or isinstance(
                position,
                int))

        if position in ['start', 'end']:
            assert(article and paragraph)
            if position == 'start':
                self.sentences[article][paragraph].insert(0, new_period)
            else:
                self.append_period(new_period, article, paragraph)

            return self.serialize()

        elif isinstance(position, int):
            self.sentences[article][paragraph].insert(position, new_period)
            return self.serialize()
        else:
            search_all = (article is None)

            if article:
                delegate_articles = [str(article)]

                if paragraph:
                    delegate_paragraphs = [str(paragraph)]
                else:
                    delegate_paragraphs = self.sentences[article].keys()
            else:
                delegate_articles = self.sentences.keys()

            for article in delegate_articles:
                if search_all:
                    delegate_paragraphs = self.sentences[article].keys()

                for paragraph in delegate_paragraphs:
                    for i, period in enumerate(
                            self.sentences[article][paragraph]):
                        if period == old_period or old_period == period[:-1]:
                            if position == 'before':
                                self.sentences[article][paragraph].insert(
                                    max(0, i - 1), new_period)
                                return self.serialize()

                            elif position == 'after':
                                self.sentences[article][paragraph].insert(
                                    i + 1, new_period)
                                return self.serialize()

        return self.serialize()

    def append_period(self, content, article, paragraph):
        """Append period to article and paragraph
        :params context : The period content
        :params article : Article number
        :params paragraph : Paragraph number
        """
        assert(article and paragraph)
        article, paragraph = str(article), str(paragraph)
        self.sentences[article][paragraph].append(content)

    def set_title(self, content, article):
        """Set title of article
        :params content : Actual title
        :params article_id : Article number
        """
        assert(article)
        article = str(article)
        self.titles[article] = content
        return self.serialize()

    def delete_title(self, article):
        """Delete the title of an article
        :param article : The article id
        """
        assert(article)
        article = str(article)
        del self.titles[article]
        return self.serialize()

    def renumber_article(self, old_id, new_id):
        """Renumber article to new id"""
        assert(article)
        self.sentences[new_id] = copy.deepcopy(self.sentences[old_id])
        del self.sentences[old_id]
        return self.serialize()

    def renumber_paragraph(self, article, old_id, new_id):
        """Renumber paragraph to new id"""
        assert(article)
        self.sentences[article][new_id] = copy.deepcopy(
            self.sentences[article][old_id])
        del self.sentences[article][old_id]
        return self.serialize()

    def delete(self):
        self.sentences = {}
        self.titles = {}
        return self.serialize()

    def apply_amendment(self, s, is_removal=False, throw_exceptions=False):
        """Applies amendment given a string s
        params s: Query string
        params throw_exceptions: Throw exceptions upon unsucessfull operations
        """
        detected = 0
        applied = 0

        if is_removal:
            trees, exc = syntax.ActionTreeGenerator.detect_removals(s)
        else:
            trees = syntax.ActionTreeGenerator.generate_action_tree_from_string(s)
        for t in trees:
            detected = 1
            try:
                if t['law']['_id'] == self.identifier:
                    self.query_from_tree(t)
                    applied = 1
            except BaseException:
                if throw_exceptions:
                    raise UnrecognizedAmendmentException(t)
        return detected, applied, self

    def query_from_tree(self, tree):
        """Returns a serizlizable object from a tree in nested form
        :params tree : A query tree generated from syntax.py
        """
        # Additive / Modifying actions
        if tree['root']['action'] in [
            'προστίθεται', 'προστίθενται',
            'αντικαθίσταται', 'αντικαθίστανται',
                'τροποποιείται', 'τροποποιούνται']:

            try:
                content = tree['what']['content']
                context = tree['what']['context']
            except KeyError:
                raise Exception('Unable to find content or context in tree')

            if context in ['άρθρο', 'άρθρα', 'article']:
                if not tree['article']['_id'].isdigit():
                    tree['article']['_id'] = self.get_next_article()
                return self.add_article(
                    article=tree['article']['_id'],
                    content=content)

            elif context in ['παράγραφος', 'παράγραφοι', 'paragraph']:
                if not tree['paragraph']['_id'].isdigit():
                    tree['article']['_id'] = self.get_next_paragraph(tree['article']['_id'])
                return self.add_paragraph(
                    article=tree['article']['_id'],
                    paragraph=tree['paragraph']['_id'],
                    content=content)

            elif context in ['εδάφιο', 'εδάφια']:
                if tree['root']['action'] in ['προστίθεται', 'προστίθενται']:
                    try:
                        pos = int(tree['period']['_id']) - 1
                    except:
                        pos = tree['period']['_id']
                    return self.insert_period(
                        position=pos,
                        old_period='',
                        new_period=content,
                        article=tree['article']['_id'],
                        paragraph=tree['paragraph']['_id'])
                elif tree['root']['action'] in ['αντικαθίσταται', 'αντικαθίστανται', 'τροποποιείται', 'τροποποιούνται']:
                    try:
                        pos = int(tree['period']['_id']) - 1
                    except:
                        pos = tree['period']['_id']

                    return self.replace_period(
                        old_period='',
                        new_period=content,
                        position=pos,
                        article=tree['article']['_id'],
                        paragraph=tree['paragraph']['_id'])
            elif context in ['φράση', 'φράσεις', 'phrase']:
                if tree['root']['action'] in ['προστίθεται', 'προστίθενται']:
                    return self.insert_phrase(
                        new_phrase=tree['phrase']['new_phrase'],
                        position=tree['phrase']['location'],
                        old_phrase=tree['phrase']['old_phrase'],
                        article=tree['article']['_id'],
                        paragraph=tree['paragraph']['_id']
                    )
                elif tree['root']['action'] in ['αντικαθίσταται', 'αντικαθίστανται']:
                    return self.replace_phrase(
                        old_phrase=tree['phrase']['old_phrase'],
                        new_phrase=tree['phrase']['new_phrase'],
                        article=tree['article']['_id'],
                        paragraph=tree['paragraph']['_id'])

            elif context in ['τίτλος', 'τίτλοι', 'title']:
                return self.set_title(
                    content=content,
                    article=tree['article']['_id']
                )
            elif context in ['περίπτωση', 'περιπτώσεις', 'υποπερίπτωση', 'υποπεριπτώσεις', 'case']:
                if context in ['περίπτωση', 'περιπτώσεις', 'case']:
                    case_letter = tree['case']['_id']
                else:
                    case_letter = tree['subcase']['_id']

                if tree['root']['action'] in ['προστίθεται', 'προστίθενται']:
                    return self.insert_case(
                        case_letter=case_letter,
                        content=content,
                        article=tree['article']['_id'],
                        paragraph=tree['paragraph']['_id']
                    )

                elif tree['root']['action'] in [
                        'αντικαθίσταται',
                        'αντικαθίστανται',
                        'τροποποιείται',
                        'τροποποιούνται']:

                    return self.replace_case(
                        case_letter=case_letter,
                        new_content=content,
                        article=tree['article']['_id'],
                        paragraph=tree['paragraph']['_id']
                    )

        # Deleting Actions
        elif tree['root']['action'] in [
            'διαγράφεται', 'διαγράφονται',
                'καταργείται', 'καταργούνται']:

            try:
                context = tree['what']['context']
            except KeyError:
                raise Exception('Unable to find context in tree')

            if context == 'law':
                print('delete self')
                return self.delete()

            elif context in ['άρθρο', 'άρθρα', 'article']:
                return self.remove_article(
                    article=tree['article']['_id']
                )
            elif context in ['παράγραφος', 'παράγραφοι', 'paragraph']:
                return self.remove_paragraph(
                    article=tree['article']['_id'],
                    paragraph=tree['paragraph']['_id']
                )
            elif context in ['εδάφιο', 'εδάφια', 'period']:
                if tree['period']['_id']:
                    return self.remove_period(
                        old_period='',
                        position=int(tree['period']['_id']) - 1,
                        article=tree['article']['_id'],
                        paragraph=tree['paragraph']['_id']
                    )
            elif context in ['φράση', 'φράσεις', 'λέξη', 'λέξεις', 'phrase']:
                return self.remove_phrase(
                    old_phrase=tree['phrase']['old_phrase'],
                    article=tree['article']['_id'],
                    paragraph=tree['paragraph']['_id']
                )

            elif context in ['περίπτωση', 'περιπτώσεις', 'υποπερίπτωση', 'υποπεριπτώσεις', 'case', 'subcase']:
                if context in ['περίπτωση', 'περιπτώσεις']:
                    case_letter = tree['case']['_id']
                else:
                    case_letter = tree['subcase']['_id']

                return self.delete_case(
                    case_letter=case_letter,
                    article=tree['article']['_id'],
                    paragraph=tree['paragraph']['_id']
                )
            else:
                raise UnsupportedOperationException(tree)

        # Renumbering Actions
        elif tree['root']['action'] in ['αναριθμείται', 'αναριθμούνται']:
            try:
                context = tree['what']['context']
            except KeyError:
                raise Exception('Unable to find context in tree')

            if context in ['άρθρο', 'άρθρα', 'article']:
                return self.renumber_article(
                    tree['article']['_id'],
                    tree['what']['to']
                )
            elif context in ['παράγραφος', 'παράγραφοι', 'paragraph']:
                return self.renumber_paragraph(
                    tree['article']['_id'],
                    tree['paragraph']['_id'],
                    tree['what']['to']
                )
            elif context in ['περίπτωση', 'περιπτώσεις', 'υποπεριπτώση', 'υποπεριπτώσεις', 'case', 'subcase']:
                if context in ['περίπτωση', 'περιπτώσεις']:
                    case_letter = tree['case']['_id']
                else:
                    case_letter = tree['subcase']['_id']

                return self.renumber_case(
                    case_letter=case_letter,
                    article=tree['article']['_id'],
                    paragraph=tree['paragraph']['_id'],
                    new_letter=tree['what']['to'])
            else:
                raise UnsupportedOperationException(tree)

        return self.serialize()

    def get_paragraph(self, article, paragraph_id):
        """Join sentences to paragraph
        :params article : Article number
        :params paragraph_id : Paragraph ID
        """
        try:
            return '. '.join(self.sentences[article][paragraph_id]).rstrip('.') + '.'
        except:
            self.sentences[article][paragraph_id] = list(filter(
                lambda p: p != None, self.sentences[article][paragraph_id]
            ))
        finally:
            return '. '.join(self.sentences[article][paragraph_id]).rstrip('.') + '.'


    def get_paragraphs(self, article):
        """Return Paragraphs via a generator
        :params article : The article number
        """
        def _get_par(x):
            try:
                return int(x.strip(')'))
            except:
                return 100

        article = str(article)
        for paragraph_id in sorted(
                self.sentences[article].keys(),
                key=_get_par):
            yield self.get_paragraph(article, paragraph_id)

    def get_articles_sorted(self):
        """Returns the articles of the statute sorted"""
        return sorted(self.sentences.keys(), key=lambda x: int(x))

    def export_law(self, export_type='markdown', add_titles=True):
        """Get law string in LaTeX, Markdown, string, plaintext and Issue-like format
        :param identifier : Law identifier
        """
        if export_type not in [
            'latex',
            'markdown',
            'str',
            'plaintext',
                'issue']:
            raise Exception('Unrecognized export type')

        if export_type == 'latex':
            result = '\chapter*{{ {} }}'.format(self.identifier)
            for article in self.get_articles_sorted():
                result = result + \
                    '\subsection*{{ Άρθρο {} }}\n'.format(article)
                for i, paragraph in enumerate(self.get_paragraphs(article)):
                    result = result + '\paragraph {{ {}. }} {}\n'.format(
                        i, paragraph)
        elif export_type == 'markdown':

            result = '# {}\n'.format(self.identifier)
            for article in self.get_articles_sorted():
                result = result + '### Άρθρο {} \n'.format(article)
                if add_titles:
                    try:
                        result = result + '#### {}\n'.format(self.titles[article])
                    except:
                        pass
                for i, paragraph in enumerate(self.get_paragraphs(article)):
                    result = result + \
                        ' {}. {}\n'.format(i, paragraph)

        elif export_type == 'str':
            result = ''
            for article in self.get_articles_sorted():
                result = result + 'Άρθρο {} '.format(article)
                for i, paragraph in enumerate(self.get_paragraphs(article)):
                    result = result + '{}'.format(paragraph)

        elif export_type == 'plaintext':

            result = ''
            for article in self.get_articles_sorted():
                result = result + 'Άρθρο {} \n'.format(article)
                if add_titles:
                    try:
                        result = result + '{}\n'.format(self.titles[article])
                    except:
                        pass
                for i, paragraph in enumerate(self.get_paragraphs(article)):
                    result = result + \
                        ' {}. {}\n'.format(i + 1, paragraph)

        elif export_type == 'issue':
            abbreviations = {
                'ν.': 'ΝΌΜΟΣ',
                'π.δ.': 'ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ',
                'ν.δ.': 'ΝΟΜΟΘΕΤΙΚΟ ΔΙΑΤΑΓΜΑ'
            }
            result = ''

            for key, val in abbreviations.items():
                if self.identifier.lower().startswith(key):
                    counter = self.identifier.strip(key).split('/')[-2]
                    result = '{} ΥΠ’ ΑΡΙΘΜ. {}\n'.format(val, counter)
                    break

            result = result + self.export_law('plaintext')

        return result

    def prune_title(self, article):
        self.titles[article] = re.sub(
            'Άρθρο \d+', '', self.titles[article]).lstrip()
        return self.titles[article]

    def prune_titles(self):
        for title in self.titles:
            self.prune_title(title)

    def get_next_article(self):
        maximum = max([int(x) for x in self.sentences.keys()])
        return str(maximum + 1)

    def get_next_paragraph(self, article):
        maximum = max([int(x) for x in self.sentences[article].keys()])
        return str(maximum + 1)


class UnsupportedOperationException(Exception):
    def __init__(self, tree):
        super().__init__(
            'Uncategorized operation on\n', json.dumps(
                tree, ensure_ascii=False))


class UnrecognizedAmendmentException(Exception):
    def __init__(self, tree):
        super().__init__(
            'Uncategorized amendment on\n', json.dumps(
                tree, ensure_ascii=False))
