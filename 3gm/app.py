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

import parser

p = parser.LawParser('nfd')
@app.route('/')
def in():
	return 'hello'
	

if __name__ == '__main__':
    app.jinja_env.globals.update(render_badges=render_badges)
    sys.setdefaultencoding('utf-8')
    app.run(debug=True, host='0.0.0.0')
