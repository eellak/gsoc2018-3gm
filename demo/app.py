from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import Markup

import json
import sys
import markdown

import collections
sys.path.insert(0, '../3gm')
from codifier import *
autocomplete_laws = sorted(list(codifier.keys()))

import networkx
from networkx.readwrite import json_graph
from networkx import (
    draw,
    DiGraph,
    Graph,
)

try:
    import spacy
    from spacy import displacy
    import el_unnamed
    nlp = el_unnamed.load()
except ImportError:
    pass

import syntax

app = Flask(__name__)
codifier_keys = codifier.keys()


@app.route('/syntax', defaults={'js': 'plain'})
@app.route('/syntax<any(plain, jquery, fetch):js>')
def index(js):
    example = '''Στο τέλος του άρθρου 5 της από 24.12.1990 Πράξης Νομοθετικού Περιεχομένου «Περί Μουσουλμάνων Θρησκευτικών Λειτουργών» (Α΄182) που κυρώθηκε με το άρθρο μόνο του ν. 1920/1991 (Α΄11) προστίθεται παράγραφος 4 ως εξής:  «4.α. Οι υποθέσεις της παραγράφου 2 ρυθμίζονται από τις κοινές διατάξεις και μόνο κατ’ εξαίρεση υπάγονται στη δικαιοδοσία του Μουφτή, εφόσον αμφότερα τα διάδικα μέρη υποβάλουν σχετική αίτησή τους ενώπιόν του για επίλυση της συγκεκριμένης διαφοράς κατά τον Ιερό Μουσουλμανικό Νόμο. Η υπαγωγή της υπόθεσης στη δικαιοδοσία του Μουφτή είναι αμετάκλητη και αποκλείει τη δικαιοδοσία των τακτικών δικαστηρίων για τη συγκεκριμένη διαφορά. Εάν οποιοδήποτε από τα μέρη δεν επιθυμεί την υπαγωγή της υπόθεσής του στη δικαιοδοσία του Μουφτή, δύναται να προσφύγει στα πολιτικά δικαστήρια, κατά τις κοινές ουσιαστικές και δικονομικές διατάξεις, τα οποία σε κάθε περίπτωση έχουν το τεκμήριο της δικαιοδοσίας.  β. Με προεδρικό διάταγμα που εκδίδεται με πρόταση των Υπουργών Παιδείας, Έρευνας και Θρησκευμάτων και Δικαιοσύνης, Διαφάνειας και Ανθρωπίνων Δικαιωμάτων καθορίζονται όλοι οι αναγκαίοι δικονομικοί κανόνες για τη συζήτηση της υπόθεσης ενώπιον του Μουφτή και την έκδοση των αποφάσεών του και ιδίως η διαδικασία υποβολής αιτήσεως των μερών, η οποία πρέπει να περιέχει τα στοιχεία των εισαγωγικών δικογράφων κατά τον Κώδικα Πολιτικής Δικονομίας και, επί ποινή ακυρότητας, ρητή ανέκκλητη δήλωση κάθε διαδίκου περί  επιλογής της συγκεκριμένης δικαιοδοσίας, η παράσταση των πληρεξουσίων δικηγόρων, η διαδικασία κατάθεσης και επίδοσής της στο αντίδικο μέρος, η διαδικασία της συζήτησης και της έκδοσης απόφασης, τα θέματα οργάνωσης, σύστασης και διαδικασίας πλήρωσης θέσεων προσωπικού (μονίμων, ιδιωτικού δικαίου αορίστου χρόνου και μετακλητών υπαλλήλων) και λειτουργίας της σχετικής υπηρεσίας της τήρησης αρχείου, καθώς και κάθε σχετικό θέμα για την εφαρμογή του παρόντος. γ. Οι κληρονομικές σχέσεις των μελών της μουσουλμανικής μειονότητας της Θράκης ρυθμίζονται από τις διατάξεις του Αστικού Κώδικα, εκτός εάν ο διαθέτης συ- ντάξει ενώπιον συμβολαιογράφου δήλωση τελευταίας βούλησης, κατά τον τύπο της δημόσιας διαθήκης, με αποκλειστικό περιεχόμενό της τη ρητή επιθυμία του να υπαχθεί η κληρονομική του διαδοχή στον Ιερό Μουσουλμανικό Νόμο. Η δήλωση αυτή είναι ελεύθερα ανακλητή, είτε με μεταγενέστερη αντίθετη δήλωσή του ενώπιον συμβολαιογράφου είτε με σύνταξη μεταγενέστερης διαθήκης, κατά τους όρους του Αστικού Κώδικα. Ταυτόχρονη εφαρμογή του Αστικού Κώδικα και του Ιερού Μουσουλμανικού Νόμου στην κληρονομική περιουσία ή σε ποσοστό ή και σε διακεκριμένα στοιχεία αυτής απαγορεύεται.»'''

    with open('examples.md') as f:
        examples = Markup(markdown.markdown(f.read()))


    return render_template('{0}.html'.format(js), js=js, example=example, examples=examples)


@app.route('/analyze', methods=['POST'])
def analyze():
    a = request.form.get('a', '', type=str)
    result = syntax.ActionTreeGenerator.generate_action_tree_from_string(a)
    print(result)
    json_string = json.dumps(result, ensure_ascii=False)
    print(json_string)

    return jsonify(result=json_string)


@app.route('/visualize')
def visualize():
    return app.send_static_file('templates/graph.html')

@app.route('/')
@app.route('/codification')
def codification():
    global codifier
    return render_template('codification.html', laws=codifier.laws)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    global autocomplete_laws
    search = request.args.get('q')
    return jsonify(matching_results=autocomplete_laws)


@app.route('/codify_law', methods=['POST', 'GET'])
def codify_law():
    if request.method == 'POST':
        data = request.form
    elif request.method == 'GET':
        identifier = request.args.get('identifier')
        print(identifier)
        data = { 'law' : identifier }

    corpus = codifier.get_law(data['law'], export_type='markdown')

    content = Markup(markdown.markdown(corpus))
    try:
        law = codifier.laws[data['law']]
    except KeyError:
        return render_template('error.html')

    # amendments
    amendments = []

    articles = sorted(law.sentences.keys())
    print(articles)

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
            except:
                continue

    try:
        refs = codifier.links['ν. 1920/1991'].links_to
        links = codifier.links['ν. 1920/1991'].organize_by_text()
    except KeyError:
        links = {}
        refs = []

    with open('graph.json') as f:
        graphData = json.load(f)
    graphData =  json.dumps(graphData, indent=2)

    return render_template('codify_law.html', **locals())

@app.route('/graph')
def graph():
    with open('graph.json') as f:
        graphData = json.load(f)
    graphData =  json.dumps(graphData, indent=2)

    return render_template('graph.html', **locals())


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

@app.template_filter('render_badges_from_tree')
def render_badges_from_tree(tree):
    tags = [
        tree['root']['action'],
        tree['law']['_id'],
        tree['what']['context']
    ]

    return render_badges(tags)


if __name__ == '__main__':
    app.jinja_env.globals.update(render_badges=render_badges)
    app.run(debug=True, use_reloader=True, ssl_context='adhoc')
