# -*- coding: utf-8 -*-

# Flask imports
import syntax
import el_core_news_sm
import spacy
import helpers
from codifier import *
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import redirect
from flask import Markup
from flask import url_for
from flask_restful import Resource, Api, output_json

# General Imports
import json
import sys
import markdown
import pymongo
import collections
import gensim.models as g
import logging
import pprint
import copy
import difflib
logger = logging.getLogger()
logger.disabled = True

# Import local modules
sys.path.insert(0, './')

autocomplete_laws = sorted(list(codifier.keys()))
autocomplete_topics = codifier.topic_keys()
autocomplete_ = autocomplete_laws + autocomplete_topics

# NLP Related packages
#import el_small
#nlp = el_small.load()
nlp = el_core_news_sm.load()

app = Flask(__name__)
application = app  # for gunicorn

# Unicode API Wrapper


class UnicodeApi(Api):
    def __init__(self, *args, **kwargs):
        super(UnicodeApi, self).__init__(*args, **kwargs)
        self.app.config['RESTFUL_JSON'] = {'ensure_ascii': False}

        self.representations = {
            'application/json; charset=utf-8': output_json,
        }


# RestFUL API
api = UnicodeApi(app)
api_lookup = {
    'l': 'ν.',
    'pd': 'π.δ.'
}

# Get id for API


def get_id(statute_type, identifier, year):
    try:
        return '{} {}/{}'.format(api_lookup[statute_type], identifier, year)
    except:
        return '{} {}/{}'.format(statute_type, identifier, year)


class LawResource(Resource):
    def get(self, statute_type, identifier, year):
        global codifier
        _id = get_id(statute_type, identifier, year)
        for x in codifier.db.laws.find({'_id': _id}):
            return x


class HistoryResource(Resource):
    def get(self, statute_type, identifier, year):
        global codifier
        _id = get_id(statute_type, identifier, year)
        return json.dumps(
            codifier.db.get_json_from_fs(_id),
            ensure_ascii=False)


class TopicResource(Resource):
    def get(self, statute_type, identifier, year):
        global codifier
        _id = get_id(statute_type, identifier, year)
        topics = list(codifier.db.topics.find({
            'statutes': _id
        }))
        return json.dumps(topics, ensure_ascii=False)


class NamedEntityResource(Resource):
    def get(self, statute_type, identifier, year):
        global codifier
        _id = get_id(statute_type, identifier, year)
        named_entities = list(codifier.db.named_entities.find({
            'statutes': _id
        }))
        return json.dumps(named_entities, ensure_ascii=False)


class LinkResource(Resource):
    def get(self, statute_type, identifier, year):
        global codifier
        _id = get_id(statute_type, identifier, year)
        for x in codifier.db.links.find({'_id': _id}):
            return x


class SyntaxResource(Resource):
    def get(self, s):
        return syntax.ActionTreeGenerator.generate_action_tree_from_string(s)


# Endpoints
api.add_resource(
    LawResource, '/get_law/<string:statute_type>/<string:identifier>/<string:year>')
api.add_resource(
    HistoryResource, '/get_history/<string:statute_type>/<string:identifier>/<string:year>')
api.add_resource(
    LinkResource, '/get_link/<string:statute_type>/<string:identifier>/<string:year>')
api.add_resource(
    TopicResource, '/get_topic/<string:statute_type>/<string:identifier>/<string:year>')
api.add_resource(SyntaxResource, '/get_syntax/<string:s>')

# Application Routes
@app.route('/syntax', defaults={'js': 'plain'})
@app.route('/syntax<any(plain, jquery, fetch):js>')
def index(js):
    with open('../examples/examples.md', encoding='utf-8') as f:
        examples = Markup(markdown.markdown(f.read()))

    return render_template(
        '{0}.html'.format(js),
        js=js,
        examples=examples)


@app.route('/analyze', methods=['POST'])
def analyze():
    a = request.form.get('a', '', type=str)
    result = syntax.ActionTreeGenerator.generate_action_tree_from_string(
        a, nested=False)
    json_string = pprint.pformat(result)
    return jsonify(result=json_string)


@app.route('/visualize')
def visualize():
    return app.send_static_file('templates/graph.html')


@app.route('/')
@app.route('/codification')
def codification():
    """Main route used for search"""
    global codifier
    num_laws = len(codifier.laws)
    num_links = len(codifier.links)
    num_topics = len(codifier.topics)
    num_named_entities = len(codifier.named_entities)
    return render_template('codification.html', num_laws=num_laws, num_links=num_links, num_topics=num_topics, num_named_entities=num_named_entities)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    """Autocomplete in searchbar"""
    global autocomplete_
    search = request.args.get('q')
    match = list(filter(lambda x: x.startswith(search), autocomplete_))
    return jsonify(matching_results=match)


@app.route('/codify_law', methods=['POST', 'GET'])
def codify_law(identifier=None):
    """Displays the current version of the law"""
    if request.method == 'POST':
        data = request.form
        identifier = data['law'].lower()
        if (identifier not in autocomplete_laws) and (not (identifier.startswith('ν.') or identifier.startswith('π.δ.'))):
            doc = nlp(identifier)
            identifier = doc[0].lemma_
            return redirect('/label/{}/rank'.format(identifier))
        else:
            # Redirect to GET request
            return redirect(url_for('codify_law', identifier=identifier))
    elif request.method == 'GET':
        identifier = request.args.get('identifier')
        data = {'law': identifier}

    try:
        law = codifier.laws[data['law']]
        corpus = codifier.get_law(data['law'], export_type='markdown')
        is_empty = is_empty_statute(corpus)
        corpus = render_links(corpus)
        content = Markup(markdown.markdown(corpus))
    except BaseException as e:
        err = str(e)
        return render_template('error.html', **locals())

    articles = sorted(law.sentences.keys())

    try:
        topics = list(codifier.db.topics.find({
            'statutes': data['law']
        }))[0]

    except IndexError:
        topics = None

    try:
        rank_txt = str(codifier.ranking[data['law']]) + 'ος'
    except:
        rank_txt = ''

    return render_template('codify_law.html', **locals())


@app.route('/amendment', methods=['POST', 'GET'])
def amendment(identifier=None):
    """Route to demonstrate what laws does the law amend"""
    if request.method == 'POST':
        data = request.form
    elif request.method == 'GET':
        identifier = request.args.get('identifier')
        data = {'law': identifier}

    try:
        law = codifier.laws[data['law']]
    except KeyError:
        return render_template('error.html')

    # amendments
    amendments = []

    articles = sorted(law.sentences.keys())

    for article in articles:
        for paragraph in law.get_paragraphs(article):
            try:
                result = syntax.ActionTreeGenerator.generate_action_tree_from_string(
                    paragraph)
                if result != []:

                    amendment = {
                        'tree': json.dumps(result, ensure_ascii=False),
                        'paragraph': paragraph,
                        'badges': result
                    }
                    amendments.append(amendment)
            except BaseException:
                continue

    return render_template('amendment.html', **locals())


@app.route('/links', methods=['POST', 'GET'])
def links(identifier=None):
    """Route to demonstrate links to the existing law"""
    if request.method == 'POST':
        data = request.form
    elif request.method == 'GET':
        identifier = request.args.get('identifier')
        data = {'law': identifier}

    corpus = codifier.get_law(data['law'], export_type='markdown')
    corpus = render_links(corpus)
    try:
        law = codifier.laws[data['law']]
    except KeyError:
        return render_template('error.html')

    try:
        links = codifier.links[data['law']].sort()
        links = codifier.links[data['law']].organize_by_text()
    except KeyError:
        links = []

    refs = set([])
    for t, r in links:
        refs |= {r[1]}
    refs = list(refs)
    helpers.quicksort(refs, helpers.compare_statutes)

    return render_template('links.html', **locals())


@app.route('/history')
def history():
    """Displays the versioning history of a law"""
    global codifier
    identifier = request.args.get('identifier')
    history, links = codifier.get_history(identifier)

    # Get as markdown
    for x in history:
        x.content = x.export_law('markdown')
        x.is_empty = is_empty_statute(x.content)
        for y in codifier.db.summaries.find({'_id': x.amendee}):
            x.summary = y['summary']

    return render_template('history.html', **locals())


@app.route('/legal_index')
def legal_index():
    """Displays the index containing only statutes"""
    global autocomplete_laws
    indexed_list = autocomplete_laws
    helpers.quicksort(indexed_list, helpers.compare_statutes)

    current = None
    toc = []
    for law in indexed_list:
        if current == None or helpers.compare_year(law) != current:
            current = helpers.compare_year(law)
            toc.append((current, law))

    return render_template('index.html', indexed_list=indexed_list, toc=toc)


@app.route('/full_index')
def full_index():
    """Displays full linking index"""
    global codifier
    full_index = list(codifier.db.links.find())
    helpers.quicksort(full_index, lambda x,
                      y: helpers.compare_statutes(x['_id'], y['_id']))

    current = None
    toc = []
    for law in full_index:
        if current == None or helpers.compare_year(law['_id']) != current:
            current = helpers.compare_year(law['_id'])
            toc.append((current, law['_id']))

    return render_template('full_index.html', full_index=full_index, toc=toc)


@app.route('/label/<label>/<sorting>')
def label(label, sorting='rank'):
    """Label search results"""
    topics = codifier.db.topics.find({
        'keywords': label
    })

    refs = []
    for t in topics:
        refs.extend(t['statutes'])
    refs = list(set(refs))

    if sorting == 'rank':
        def _rank(x):
            try:
                return -codifier.ranks[x]
            except:
                return 0
        refs.sort(key=lambda x: _rank(x))
    elif sorting == 'chronological':
        helpers.quicksort(refs, helpers.compare_statutes)
        refs = list(reversed(refs))

    summaries = {}
    for identifier in refs:
        for x in codifier.db.summaries.find({'_id': identifier}):
            summaries[identifier] = x['summary']

    return render_template('label.html', **locals())


@app.route('/topics')
def topics():
    """Topics page"""
    topics = codifier.topics
    return render_template('topics.html', **locals())


@app.route('/diff', methods=['POST', 'GET'])
def diff():
    """Diffs page"""
    if request.method == 'POST':
        data = request.form
        print(data)
        return redirect(url_for('diff',
                                identifier=data['identifier'],
                                final=data['final'],
                                initial=data['initial']))

    global codifier
    differ = difflib.Differ()

    # Parse args
    identifier = request.args.get('identifier')
    final = request.args.get('final')
    initial = request.args.get('initial')
    history, links = codifier.get_history(identifier)

    initial_gg_link = gg_link(initial)
    final_gg_link = gg_link(final)

    initial_archive_link = archive_link(initial)
    final_archive_link = archive_link(final)

    # Get as markdown
    for x in history:
        if x.amendee == final:
            try:
                final_text = x.export_law('issue').splitlines()
            except:
                final_text = ['']
        elif x.amendee == initial:
            try:
                initial_text = x.export_law('issue').splitlines()
            except:
                initial_text = ['']

    diffs = differ.compare(initial_text, final_text)

    return render_template('diff.html', **locals())


@app.route('/help')
def help():
    """Help page"""
    return render_template('help.html', **locals())


def color_iterator():
    colors = [
        'primary',
        'secondary',
        'success',
        'light',
        'dark',
        'info',
        'danger',
        'warning']
    N = len(colors)
    i = 0
    while True:
        yield colors[i]
        i = (i + 1) % N


@app.template_filter('render_badges')
def render_badges(l):
    result = ''
    colors = color_iterator()
    for x in l:
        result = result + \
            '<span class="badge badge-{}">{}</span> '.format(next(colors), x)
    return result


@app.template_filter('render_badges_single')
def render_badges_single(l, color='light', label_url=True):
    result = ''
    for x in l:
        if label_url:
            url = url_for('label', label=x, sorting='rank')
            result = result + \
                '<span class="badge badge-{}"><a class="no-linter" href="{}">{}</a></span> '.format(
                    color, url, x)
        else:
            result = result + \
                '<span class="badge badge-{}">{}</span> '.format(color, x)
    return result


@app.template_filter('render_badges_from_tree')
def render_badges_from_tree(tree):
    try:
        what = '{} {}'.format(tree['what']['context'], tree['what']['number'])
    except BaseException:
        what = tree['what']['context']

    tags = [
        tree['root']['action'],
        tree['law']['_id'],
        what
    ]

    return render_badges(tags)


@app.template_filter('render_links')
def render_links(content):
    search_results = []
    for entity in entities.LegalEntities.entities:
        tmp = [(x.group(), x.span()[1]) for x in re.finditer(entity, content)]
        search_results.extend(tmp)
    hyperlinks = [to_hyperlink(l[0]) for l in search_results]
    splitted = helpers.split_index(content, [l[1] for l in search_results])

    i = 0
    for x, y in zip(search_results, hyperlinks):
        splitted[i] = splitted[i].replace(x[0], y)
        i += 1

    return ''.join(splitted)

# Template filters


def to_hyperlink(l, link_type='markdown'):
    u = url_for('codify_law', identifier=l)
    if link_type == 'html':
        return '''<a href="{1}">{0}</a>'''.format(l, u)
    elif link_type == 'markdown':
        return '[{0}]({1})'.format(l, u)


@app.template_filter('render_md')
def render_md(corpus):
    return Markup(markdown.markdown(corpus))


@app.template_filter('listify')
def listify(s):
    return list(s)


@app.template_filter('setify')
def setify(s):
    return set(s)


@app.template_filter('archive_link')
def archive_link(identifier):
    cur = codifier.db.archive_links.find({
        '_id': identifier
    })
    for x in cur:
        l = x['issue']

    return 'https://archive.org/details/GreekGovernmentGazette-{}'.format(l)


@app.template_filter('gg_link')
def gg_link(identifier):
    cur = codifier.db.archive_links.find({
        '_id': identifier
    })
    for x in cur:
        l = x['issue']

    return 'ΦΕΚ Α {}/{}'.format(int(l[-4:]), l[:4])


@app.template_filter('lower')
def lower(s):
    return s.lower()


@app.template_filter('highlight_diff')
def highlight_diff(d, initial, final, initial_archive, final_archive):
    lookup = {
        '+': 'rgba(0, 255, 0, 0.3)',
        '-': 'rgba(255, 0, 0, 0.3)',
        '?':  'rgba(0, 0, 255, 0.3)'
    }

    gg_lookup = {
        '+': final,
        '-': initial,
        '?': 'Δεν βρίσκεται σε κανένα από τα δύο'
    }

    archive_lookup = {
        '+': final_archive,
        '-': initial_archive,
        '?': 'Δεν βρίσκεται σε κανένα από τα δύο'
    }

    try:
        pref = "<a href='{}' class='no-linter'><p style='background-color: {};' data-toggle='tooltip' data-placement='right' data-html='true' title='<h3>{}</h3>' >{}</p></a>".format(
            archive_lookup[d[0]], lookup[d[0]], gg_lookup[d[0]], d)
        script = '''<script>
                    $(document).ready(function(){
                        $('[data-toggle="tooltip"]').tooltip();
                    });
                    </script>'''
        return pref + script
    except BaseException:
        return '<p>{}</p>'.format(d)


def is_empty_statute(s):
    return len(s.splitlines()) == 1


if __name__ == '__main__':
    app.jinja_env.globals.update(render_badges=render_badges)
    sys.setdefaultencoding('utf-8')
    app.run(debug=True, host='0.0.0.0')
