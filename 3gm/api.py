# -*- coding: utf-8 -*-

# Flask imports
import io
import sys
import syntax
import el_core_web_sm
import spacy
import helpers
from codifier import *
from archiveapi import ArchiveStats
from operator import itemgetter
from datetime import datetime, timedelta
import hashlib
import urllib
import base64
import lzma
import gzip
import difflib
import re
import copy
import pprint
import logging
import collections
import database
import pymongo
import markdown
import json
from flask import Flask
from flask import jsonify
from flask import url_for
from flask import Markup

from flask_restful import Resource, Api, output_json, request, reqparse
from flask_cors import CORS
from flask_redis import FlaskRedis

from bson import json_util
from bson.json_util import dumps, loads, DEFAULT_JSON_OPTIONS

DEFAULT_JSON_OPTIONS.datetime_representation = 2

# Caching costants
CACHE_ENABLED = True
# for redis cache set default expire time to 24 hours
CACHE_DEFAULT_EXPIRE_TIME = 86400
#DEFAULT_JSON_OPTIONS.tz_aware = False

# General Imports

# Import local modules
sys.path.insert(0, './')


#autocomplete_laws = sorted(list(codifier.keys()))
#autocomplete_topics = codifier.topic_keys()
#autocomplete_ = autocomplete_laws + autocomplete_topics

# NLP Related packages
nlp = el_core_web_sm.load()

app = Flask(__name__)
CORS(app)
app.config['REDIS_URL'] = "redis://127.0.0.1:6379/0"

api = Api(app)
redis_store = FlaskRedis(app)


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

# Get title for API


def get_title(statute_type, identifier, year):
    try:
        return '{} {}/{}'.format(api_lookup[statute_type], identifier, year)
    except:
        return '{} {}/{}'.format(statute_type, identifier, year)


def get_parts_from_title(item):
    try:
        year = int(item.split('/')[-1])
        name = int(re.sub('[^0-9]', '', item.split('/')[0]))
    except BaseException:
        year = int(item.split('.')[-1])
        name = int(re.sub('[^0-9]', '', item.split('.')[0]))
    t = "pd" if item.lower().startswith("π.δ") else "l"
    id = f"{t}_{name}_{year}"
    return id, t, name, year


def get_title_from_id(statute_id):
    return get_title(*statute_id.split('_'))


def get_id_from_title(title):
    return get_parts_from_title(title)[0]


def get_cache_key():
    args = request.view_args
    #print (args)
    s = request.path + '?' + urllib.parse.urlencode(args)
    hashkey = base64.b64encode(hashlib.md5(s.encode('utf-8')).digest())
    return hashkey


def cache_store(cache_key, val, expires=True, compress=False):
    if not val:
        return

    # dump if not string
    if not isinstance(val, str):
        val = dumps(val, json_options=json_util.RELAXED_JSON_OPTIONS,
                    ensure_ascii=False)

    if (compress):
        val = lzma.compress(val.encode("utf-8"))

    if (expires):
        redis_store.setex(cache_key, CACHE_DEFAULT_EXPIRE_TIME, val)
    else:
        redis_store.set(cache_key, val)

    return val


def cache_key_exists(cache_key):
    return CACHE_ENABLED and redis_store.exists(cache_key)


def get_topics_for_statute(statute_id):
    l = list((x['keywords']
              for x in codifier.topics if statute_id in x['statutes']))
    s = ' '.join(np.unique(np.array(l).flatten()))
    docx = nlp(s)
    e = list(set(token.lemma_ for token in docx if len(token) > 3 and token.is_stop !=
                 True and token.is_punct != True and token.pos_ == 'NOUN'))


def build_legal_index():
    if redis_store.exists("statute_index"):
        app.logger.info('getting statute index from Redis')
        return json.loads(redis_store.get('statute_index'))
    app.logger.info('getting statute index from Mongo')
    legal_index = []
    for item in list(codifier.keys()):
        try:
            id, t, name, year = get_parts_from_title(item)
            rank = codifier.ranking.get(item, -1)
            if year and year <= datetime.today().year and name > 0:
                legal_index.append(
                    {'_id': id, 'name': name, 'type': t, 'year': year, 'rank': rank})
        except:
            pass

    legal_index.sort(reverse=True, key=itemgetter('year', 'name', 'type'))
    cache_store('statute_index', legal_index, False)
    return legal_index


def to_hyperlink(l, link_type='markdown'):
    u = 'http://test/' + l
    if link_type == 'html':
        return '''<a href="{1}">{0}</a>'''.format(l, u)
    elif link_type == 'markdown':
        return '[{0}]({1})'.format(l, u)


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


legal_index = build_legal_index()

# class LawResource(Resource):
# def get(self, statute_type, identifier, year):
# global codifier
# _id = get_title(statute_type, identifier, year)
# for x in codifier.db.laws.find({'_id' : _id}):
# return x

# class HistoryResource(Resource):
# def get(self, statute_type, identifier, year):
# global codifier
# _id = get_title(statute_type, identifier, year)
# return json.dumps(
# codifier.db.get_json_from_fs(_id),
# ensure_ascii=False)

# class TopicResource(Resource):
# def get(self, statute_type, identifier, year):
# global codifier
# _id = get_title(statute_type, identifier, year)
# topics = list(codifier.db.topics.find({
# 'statutes': _id
# }))
# return json.dumps(topics, ensure_ascii=False)

# class LinkResource(Resource):
# def get(self, statute_type, identifier, year):
# global codifier
# _id = get_title(statute_type, identifier, year)
# for x in codifier.db.links.find({'_id' : _id}):
# return x

# class SyntaxResource(Resource):
# def get(self, s):
# return syntax.ActionTreeGenerator.generate_action_tree_from_string(s)


class TopicsResource(Resource):
    def get(self):
        cache_key = get_cache_key()
        if redis_store.exists(cache_key):
            app.logger.info('getting data from Redis')
            return json.loads(redis_store.get(cache_key))
        res = codifier.topics
        cache_store(cache_key, res)
        return res


class NamedEntitiesResource(Resource):
    def get(self):
        cache_key = get_cache_key()
        if redis_store.exists(cache_key):
            app.logger.info('getting data from Redis')
            return json.loads(redis_store.get(cache_key))
        res = codifier.named_entities
        cache_store(cache_key, res)
        return res


class ArchiveStatsResource(Resource):
    def get(self):
        cache_key = get_cache_key()
        if redis_store.exists(cache_key):
            app.logger.info('getting data from Redis')
            return json.loads(redis_store.get(cache_key))
        res = ArchiveStats.getStats()
        #jsonres = dumps(res,json_options=json_util.RELAXED_JSON_OPTIONS)
        cache_store(cache_key, res)
        return res


class IaStatsResource(Resource):
    def get(self):
        cache_key = get_cache_key()
        if redis_store.exists(cache_key):
            app.logger.info('getting data from Redis')
            return json.loads(redis_store.get(cache_key))
        db = database.Database()

        res_count_total = db.ia.count_documents({})
        res_count_lastyear = db.ia.count_documents(
            {'addeddate': {'$lt': datetime.now(), '$gte': datetime.now() - timedelta(days=365)}})
        res_count_lastmonth = db.ia.count_documents(
            {'addeddate': {'$lt': datetime.now(), '$gte': datetime.now() - timedelta(days=30)}})
        res_count_lastweek = db.ia.count_documents(
            {'addeddate': {'$lt': datetime.now(), '$gte': datetime.now() - timedelta(days=7)}})
        res_last_docs = list(db.ia.find(
            {}, {'identifier': 1, 'title': 1, 'addeddate': 1}).sort('addeddate', -1).limit(5))

        res = {'res_count_total': res_count_total, 'res_count_lastyear': res_count_lastyear,
               'res_count_lastmonth': res_count_lastmonth, 'res_count_lastweek': res_count_lastweek, 'res_last_docs': res_last_docs}

        #jsonres = dumps(res,json_options=json_util.RELAXED_JSON_OPTIONS)
        cache_store(cache_key, res)
        return res


class StatuteStatsResource(Resource):
    def get(self):
        cache_key = get_cache_key()
        if cache_key_exists(cache_key):
            app.logger.info('getting data from Redis')
            return json.loads(redis_store.get(cache_key))

        num_laws = len(codifier.laws)
        num_links = len(codifier.links)
        num_topics = len(codifier.topics)

        last_5_pd = list(filter(lambda x: x['type'] == 'pd', legal_index))[:5]
        last_5_laws = list(filter(lambda x: x['type'] == 'l', legal_index))[:5]

        iarchive_stats = ArchiveStats.getStats()
        res = {
            'res_laws_total': num_laws, 'res_links_total': num_links, 'res_topics_total': num_topics, 'last_5_laws': last_5_laws, 'last_5_pd': last_5_pd, 'iarchive_stats': iarchive_stats
        }

        #jsonres = dumps(res)
        cache_store(cache_key, res)
        return res


class StatuteIndexResource(Resource):
    def get(self):
        return legal_index


class StatuteResource(Resource):
    def get(self, statute_id):
        _id = get_title_from_id(statute_id)
        cache_key = get_cache_key()
        if cache_key_exists(cache_key):
            app.logger.info('getting data from Redis')
            return json.loads(redis_store.get(cache_key))

        rank = codifier.ranking.get(_id, -1)
        archive = codifier.db.archive_links.find_one(
            {'_id': _id}, {'issue': 1, '_id': 0})
        archive_issue = (archive or {}).get('issue', '')
        name, year = (int(d) for d in statute_id.split('_')[1:])
        type = statute_id.split('_')[:1][0]
        res = {'_id': statute_id, 'titleGR': _id, 'rank': rank,
               'archive': archive_issue, 'name': name, 'year': year, 'type': type}
        cache_store(cache_key, res)
        return res

# single article of statute


class StatuteArticleResource(Resource):
    def get(self, statute_id, article_id):
        _id = get_title_from_id(statute_id)

        law = codifier.laws[_id]
        article_corpus = law.sentences[article_id]

        return json.loads(json.dumps(article_corpus, ensure_ascii=True))

# all articles of statute


class StatuteArticlesResource(Resource):
    def get(self, statute_id):
        _id = get_title_from_id(statute_id)
        cache_key = get_cache_key()
        if cache_key_exists(cache_key):
            app.logger.info('getting data from Redis')
            compressed_data = redis_store.get(cache_key)
            text_data = lzma.decompress(compressed_data).decode('utf-8')
            return json.loads(text_data)

        law = codifier.laws[_id]
        articles = law.sentences
        ordered_articles = {}
        for key in sorted(articles, key=lambda x: int(x)):
            ordered_articles[key] = articles[key]
        cache_store(cache_key, ordered_articles, compress=True)
        return ordered_articles


class StatuteCodifiedResource(Resource):
    def get(self, statute_id):
        _id = get_title_from_id(statute_id)
        cache_key = get_cache_key()
        if cache_key_exists(cache_key):
            app.logger.info('getting data from Redis')
            compressed_data = redis_store.get(cache_key)
            text_data = lzma.decompress(compressed_data).decode('utf-8')
            return text_data

        law = codifier.laws[_id]
        corpus = codifier.get_law(_id, export_type='markdown')
        is_empty = len(corpus.splitlines()) == 1
        if (is_empty):
            return "<h3>Το νομοθέτημα έχει καταργθεί</h3>"
        corpus = render_links(corpus)
        res = Markup(markdown.markdown(corpus))
        cache_store(cache_key, res, compress=True)
        return res


class StatuteTopicsResource(Resource):
    def get(self, statute_id):
        _id = get_title_from_id(statute_id)
        cache_key = get_cache_key()
        if cache_key_exists(cache_key):
            app.logger.info('getting data from Redis')
            return json.loads(redis_store.get(cache_key))

        topics = list(codifier.db.topics.find({'statutes': _id}))
        if len(topics) > 0:
            topics = topics[0]
            cache_store(cache_key, topics)
        return topics


class StatuteNamedEntitiesResource(Resource):
    def get(self, statute_id):
        _id = get_title_from_id(statute_id)
        cache_key = get_cache_key()
        if cache_key_exists(cache_key):
            app.logger.info('getting data from Redis')
            return json.loads(redis_store.get(cache_key))

        named_entities = list(
            codifier.db.named_entities.find({'statutes': _id}))
        if len(named_entities) > 0:
            named_entities = named_entities[0]
            cache_store(cache_key, named_entities)
        return named_entities


class StatuteRankingResource(Resource):
    def get(self, statute_id):
        statute = next(
            filter(lambda d: d['_id'] == statute_id, legal_index), None)
        res = -1 if statute is None else statute['rank']
        return res


class StatuteHistoryResource(Resource):
    def get(self, statute_id):
        global codifier
        _id = get_title_from_id(statute_id)
        history, links = codifier.get_history(_id)

        jsonres = []
        for law in reversed(history):
            res = {}

            res['identifier'] = get_id_from_title(law.identifier)
            res['amendee'] = get_id_from_title(law.amendee)

            amendee_year = get_parts_from_title(law.amendee)[3]
            res['amendee_date'] = f'01-01-{amendee_year}'

            res['issue'] = law.issue
            res['summary'] = codifier.db.summaries.find_one(
                {'_id': law.amendee}, {'summary': 1, '_id': 0})['summary']
            res['archive'] = codifier.db.archive_links.find_one(
                {'_id': law.amendee}, {'issue': 1, '_id': 0})['issue']
            jsonres.append(res)

        return json.loads(json.dumps(jsonres, ensure_ascii=True))


class StatuteLinksResource(Resource):
    def get(self, statute_id):
        _id = get_title_from_id(statute_id)
        cache_key = get_cache_key()
        if cache_key_exists(cache_key):
            app.logger.info('getting data from Redis')
            return json.loads(redis_store.get(cache_key))
        law = codifier.laws[_id]
        links = codifier.links[_id].organize_by_text()
        articles = sorted(law.sentences.keys())
        refs = dict()
        amendments = dict()

        for t, r in links:
            statute = r[1]
            item = (r[0], r[2])
            refs.setdefault(statute, set([])).add(item)

        for article in articles:
            for paragraph in law.get_paragraphs(article):
                try:
                    result = syntax.ActionTreeGenerator.generate_action_tree_from_string(
                        paragraph)
                    if result != []:
                        for found in result:
                            if 'law' in found['root']['children'] and found['law']['_id']:
                                statute = found['law']['_id']
                                item = (found['root']['action'],
                                        found['what']['context'])
                                amendments.setdefault(
                                    statute, set([])).add(item)
                except BaseException:
                    continue
        res = {'incoming': refs, 'outgoing': amendments}
        #strres = dumps( res , ensure_ascii=False)
        str_res = cache_store(cache_key, res)
        return json.loads(str_res)


class StatuteDiffResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('stripcontext', type=str)
        super(StatuteDiffResource, self).__init__()

    def get(self, statute_id, amendee_id):
        _id = _initial = get_title_from_id(statute_id)
        _final = get_title_from_id(amendee_id)

        history, links = codifier.get_history(_id)

        version_initial = next(
            (x for x in history if x.amendee == _initial), None)
        version_final = next((x for x in history if x.amendee == _final), None)
        if version_initial and version_final:
            # parse params

            args = self.reqparse.parse_args(strict=True)

            initial_text = version_initial.export_law(
                'issue').splitlines(keepends=True)
            final_text = version_final.export_law(
                'issue').splitlines(keepends=True)

            n = 1000 if not args.get('stripcontext', 'false') == 'true' else 5
            diffs = difflib.unified_diff(
                initial_text, final_text, fromfile=_id, tofile=_final, n=n)
            #diffs = difflib.context_diff(initial_text, final_text , fromfile=_id, tofile=_final)
            res = list(diffs)

        return res  # json.loads(json.dumps(jsonres, ensure_ascii=True))

# Control Commands


class RedisFlushResource(Resource):
    def get(self, statute_id):
        redis_store.flushdb()
        return "ok"

# Endpoints


# Statutes
api.add_resource(StatuteIndexResource, '/statute/index')
api.add_resource(StatuteStatsResource, '/statute/stats')

api.add_resource(StatuteResource, '/statute/<string:statute_id>')
api.add_resource(StatuteCodifiedResource,
                 '/statute/<string:statute_id>/codified')
api.add_resource(StatuteHistoryResource,
                 '/statute/<string:statute_id>/history')
api.add_resource(StatuteLinksResource, '/statute/<string:statute_id>/links')
api.add_resource(StatuteDiffResource,
                 '/statute/diff/<string:statute_id>/<string:amendee_id>')

api.add_resource(StatuteArticlesResource,
                 '/statute/<string:statute_id>/articles')
api.add_resource(StatuteArticleResource,
                 '/statute/<string:statute_id>/articles/<string:article_id>')

api.add_resource(StatuteTopicsResource, '/statute/<string:statute_id>/topics')
api.add_resource(StatuteNamedEntitiesRecource,
                 '/statute/<string:statute_id>/named_entities')
api.add_resource(StatuteRankingResource,
                 '/statute/<string:statute_id>/ranking')

# Topics
api.add_resource(TopicsResource, '/topics')

# Named Entities
api.add_resource(NamedEntitiesResource, '/named_entities')

# Internet archive
api.add_resource(ArchiveStatsResource, '/ia/stats')

# Control
api.add_resource(RedisFlushResource, '/admin/flushcache')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
