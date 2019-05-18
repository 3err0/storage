#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import random
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, jsonify

from flask.ext.restful import Api, Resource
from flask.ext.restful.reqparse import RequestParser, Argument
from werkzeug.datastructures import FileStorage

app = Flask(__name__)
api = Api(app)
app.config.from_object(__name__)

CURRENT_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(CURRENT_DIR, 'uploads')

ALLOWED_EXTENSIONS = ['txt', 'pdf', 'doc', 'xls',
                      'png', 'jpg', 'jpeg', 'gif',
                      'avi', '3gp', 'flv', 'mp4',
                      'rar', 'zip', 'gz', 'deb']

def upload(file):
    if file and allowed_file(file.filename):
        filename = generate_filename(file.filename)
        file.save(os.path.join(UPLOAD_DIR, filename))
        return filename

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == 'POST':
        filename = upload(request.files['file'])
        if filename:
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template("index.html")

class api_upload(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('image', type=FileStorage, location='files')
        parser.add_argument('file', type=FileStorage, location='files')
        args = parser.parse_args()
        file = args['image'] or args['file']
        if not file:
            return jsonify({'error': 'not file for upload'})
        else:
            filename = upload(file)
            return jsonify({'href': '%s%s' % (request.url_root, filename)})

@app.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

def generate_filename(filename, length=8):
    'Generates a unique file name containing a-z A-Z 0-9'
    pool = range(48, 57) + range(65, 90) + range(97, 122)
    name = ''.join(chr(random.choice(pool)) for _ in range(length))
    filename = "%s.%s" % (name, filename.rsplit('.', 1)[1])
    return filename

def allowed_file(filename):
    return '.' in filename \
           and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

api.add_resource(api_upload, '/upload')

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, mode=0777)
    app.run('0.0.0.0', debug=True)
