#!/bin/bash
export FLASK_APP=app.py &&
export FLASK_DEBUG=1 &&
flask run --port=5001 &
