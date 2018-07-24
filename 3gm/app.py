# -*- coding: utf-8 -*-

# Flask imports
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
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
logger = logging.getLogger()
logger.disabled = True


global doc2vec


# Import local modules
sys.path.insert(0, './')

from codifier import *
import helpers
autocomplete_laws = sorted(list(codifier.keys()))


try:
    import spacy
    import el_spacy
    nlp = el_small.load()
except ImportError:
    pass

import syntax

app = Flask(__name__)
application = app # for gunicorn

class UnicodeApi(Api):
    def __init__(self, *args, **kwargs):
        super(UnicodeApi, self).__init__(*args, **kwargs)
        self.app.config['RESTFUL_JSON'] = { 'ensure_ascii': False }

        self.representations = {
            'application/json; charset=utf-8': output_json,
        }

# RestFUL API
api = UnicodeApi(app)

class LawResource(Resource):
    def get(self, identifier):
        global codifier
        for x in codifier.db.laws.find({'_id' : identifier}):
            return x

class LinkResource(Resource):
    def get(self, identifier):
        global codifier
        for x in codifier.db.links.find({'_id' : identifier}):
            return x

class SyntaxResource(Resource):
    def get(self, s):
        return syntax.ActionTreeGenerator.generate_action_tree_from_string(s)


api.add_resource(LawResource, '/get_law/<string:identifier>')
api.add_resource(LinkResource, '/get_link/<string:identifier>')
api.add_resource(SyntaxResource, '/syntax_api/<string:s>')

# Application
@app.route('/syntax', defaults={'js': 'plain'})
@app.route('/syntax<any(plain, jquery, fetch):js>')
def index(js):
    example = '''Στο τέλος του άρθρου 5 της από 24.12.1990 Πράξης Νομοθετικού Περιεχομένου «Περί Μουσουλμάνων Θρησκευτικών Λειτουργών» (Α΄182) που κυρώθηκε με το άρθρο μόνο του ν. 1920/1991 (Α΄11) προστίθεται παράγραφος 4 ως εξής:  «4.α. Οι υποθέσεις της παραγράφου 2 ρυθμίζονται από τις κοινές διατάξεις και μόνο κατ’ εξαίρεση υπάγονται στη δικαιοδοσία του Μουφτή, εφόσον αμφότερα τα διάδικα μέρη υποβάλουν σχετική αίτησή τους ενώπιόν του για επίλυση της συγκεκριμένης διαφοράς κατά τον Ιερό Μουσουλμανικό Νόμο. Η υπαγωγή της υπόθεσης στη δικαιοδοσία του Μουφτή είναι αμετάκλητη και αποκλείει τη δικαιοδοσία των τακτικών δικαστηρίων για τη συγκεκριμένη διαφορά. Εάν οποιοδήποτε από τα μέρη δεν επιθυμεί την υπαγωγή της υπόθεσής του στη δικαιοδοσία του Μουφτή, δύναται να προσφύγει στα πολιτικά δικαστήρια, κατά τις κοινές ουσιαστικές και δικονομικές διατάξεις, τα οποία σε κάθε περίπτωση έχουν το τεκμήριο της δικαιοδοσίας.  β. Με προεδρικό διάταγμα που εκδίδεται με πρόταση των Υπουργών Παιδείας, Έρευνας και Θρησκευμάτων και Δικαιοσύνης, Διαφάνειας και Ανθρωπίνων Δικαιωμάτων καθορίζονται όλοι οι αναγκαίοι δικονομικοί κανόνες για τη συζήτηση της υπόθεσης ενώπιον του Μουφτή και την έκδοση των αποφάσεών του και ιδίως η διαδικασία υποβολής αιτήσεως των μερών, η οποία πρέπει να περιέχει τα στοιχεία των εισαγωγικών δικογράφων κατά τον Κώδικα Πολιτικής Δικονομίας και, επί ποινή ακυρότητας, ρητή ανέκκλητη δήλωση κάθε διαδίκου περί  επιλογής της συγκεκριμένης δικαιοδοσίας, η παράσταση των πληρεξουσίων δικηγόρων, η διαδικασία κατάθεσης και επίδοσής της στο αντίδικο μέρος, η διαδικασία της συζήτησης και της έκδοσης απόφασης, τα θέματα οργάνωσης, σύστασης και διαδικασίας πλήρωσης θέσεων προσωπικού (μονίμων, ιδιωτικού δικαίου αορίστου χρόνου και μετακλητών υπαλλήλων) και λειτουργίας της σχετικής υπηρεσίας της τήρησης αρχείου, καθώς και κάθε σχετικό θέμα για την εφαρμογή του παρόντος. γ. Οι κληρονομικές σχέσεις των μελών της μουσουλμανικής μειονότητας της Θράκης ρυθμίζονται από τις διατάξεις του Αστικού Κώδικα, εκτός εάν ο διαθέτης συ- ντάξει ενώπιον συμβολαιογράφου δήλωση τελευταίας βούλησης, κατά τον τύπο της δημόσιας διαθήκης, με αποκλειστικό περιεχόμενό της τη ρητή επιθυμία του να υπαχθεί η κληρονομική του διαδοχή στον Ιερό Μουσουλμανικό Νόμο. Η δήλωση αυτή είναι ελεύθερα ανακλητή, είτε με μεταγενέστερη αντίθετη δήλωσή του ενώπιον συμβολαιογράφου είτε με σύνταξη μεταγενέστερης διαθήκης, κατά τους όρους του Αστικού Κώδικα. Ταυτόχρονη εφαρμογή του Αστικού Κώδικα και του Ιερού Μουσουλμανικού Νόμου στην κληρονομική περιουσία ή σε ποσοστό ή και σε διακεκριμένα στοιχεία αυτής απαγορεύεται.»'''

    with open('../examples/examples.md', encoding='utf-8') as f:
        examples = Markup(markdown.markdown(f.read()))

    return render_template(
        '{0}.html'.format(js),
        js=js,
        example=example,
        examples=examples)


@app.route('/analyze', methods=['POST'])
def analyze():
    a = request.form.get('a', '', type=str)
    result = syntax.ActionTreeGenerator.generate_action_tree_from_string(a, nested=False)
    json_string = json.dumps(result, ensure_ascii=False)
    return jsonify(result=json_string)


@app.route('/visualize')
def visualize():
    return app.send_static_file('templates/graph.html')


@app.route('/')
@app.route('/codification')
def codification():
    global codifier
    num_laws = len(codifier.laws)
    num_links = len(codifier.links)
    num_topics = len(codifier.topics)
    return render_template('codification.html', num_laws=num_laws, num_links=num_links, num_topics=num_topics)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    global autocomplete_laws
    search = request.args.get('q')
    match = list(filter(lambda x: x.startswith(search), autocomplete_laws))
    return jsonify(matching_results=match)


@app.route('/codify_law', methods=['POST', 'GET'])
def codify_law(identifier=None):
    if request.method == 'POST':
        data = request.form
    elif request.method == 'GET':
        identifier = request.args.get('identifier')
        data = {'law': identifier}

    corpus = codifier.get_law(data['law'], export_type='markdown')
    corpus = render_links(corpus)
    content = Markup(markdown.markdown(corpus))
    try:
        law = codifier.laws[data['law']]
    except KeyError:
        return render_template('error.html')

    articles = sorted(law.sentences.keys())

    try:
        topics = list(codifier.db.topics.find({
            'statutes': data['law']
        }))[0]

    except IndexError:
        topics = None


    return render_template('codify_law.html', **locals())

@app.route('/amendment', methods=['POST', 'GET'])
def amendment(identifier=None):
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
    global codifier
    identifier = request.args.get('identifier')
    history, links = codifier.get_history(identifier)

    if links:
        links = links.organize_by_text()

    # Get as markdown
    for x in history:
        x.content = x.export_law('markdown')

    return render_template('history.html', **locals())


@app.route('/legal_index')
def legal_index():
    global autocomplete_laws
    return render_template('index.html', indexed_list=autocomplete_laws)


@app.route('/full_index')
def full_index():
    global codifier
    full_index = codifier.db.links.find().sort('_id', pymongo.ASCENDING)

    return render_template('full_index.html', full_index=full_index)


@app.route('/docs/<page>')
def docs(page):
    return render_template('docs/' + page + '.html')

@app.route('/display_cards/<filename>')
def display_cards(filename):
    with open(filename, encoding='utf-8') as f:
        contents = f.read().splitlines()
    return render_template('display_cards.html', **locals())

@app.route('/help')
def help():
    with open('templates/help.md', encoding='utf-8') as f:
        help = f.read()
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
def render_badges_single(l, color='light'):
    result = ''
    for x in l:
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
def archive_link(l):
    return 'https://archive.org/details/GreekGovernmentGazette-{}'.format(l)

if __name__ == '__main__':
    app.jinja_env.globals.update(render_badges=render_badges)
    sys.setdefaultencoding('utf-8')
    app.run(debug=True, host='0.0.0.0')
