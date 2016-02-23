#!/usr/bin/python
# Copyright Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# coding: -*- utf-8 -*-

from google.appengine.ext import vendor
vendor.add('lib')

import json

from flask import Flask
from flask import render_template
from flask import session
from flask import request
from flask import make_response

from apiclient.discovery import build
from oauth2client import client, crypt
import httplib2

from google.appengine.ext import ndb


app = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)
app.config.update(
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_PATH='/'
)
app.debug = True

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
app.secret_key = 'abcde'


class CredentialStore(ndb.Model):
    id_token = ndb.JsonProperty()
    credentials = ndb.JsonProperty()

    @classmethod
    def remove(cls, key):
        ndb.Key(cls.__name__, key).delete()


@app.route('/')
def index():
    mode = request.args.get('mode', '')
    # Sanitize `mode` parameter
    if mode not in {'introduction',
                    'authentication_with_backends',
                    'authorization_client',
                    'authorization_server'}:
        mode = 'introduction'

    return render_template('index.html', client_id=CLIENT_ID, mode=mode)


@app.route('/api')
def api():
    if 'id' not in session:
        return make_response('Not authenticated', 401)

    sub = session.get('id')
    store = CredentialStore.get_by_id(sub)

    if store.credentials is None:
        # Not authorized for offline use
        return make_response('access_token not stored', 401)

    credentials = client.Credentials.new_from_json(store.credentials)
    http = credentials.authorize(httplib2.Http())
    drive = build('drive', 'v3', http=http)
    files = drive.files().list(fields='files').execute()

    return make_response(json.dumps(files.get('files', [])), 200)


@app.route('/validate', methods=['POST'])
def validate():
    id_token = request.form.get('id_token', '')
    idinfo = client.verify_id_token(id_token, CLIENT_ID)

    if idinfo['aud'] != CLIENT_ID:
        return make_response('Wrong Audience.', 401)
    if idinfo['iss'] not in ['accounts.google.com',
                             'https://accounts.google.com']:
        return make_response('Wrong Issuer.', 401)

    sub = idinfo['sub']
    store = CredentialStore(id=sub, id_token=idinfo)
    store.put()

    session['id'] = sub

    return make_response('', 200)


@app.route('/code', methods=['POST'])
def code():
    code = request.form.get('code', '')
    try:
        credentials = client.credentials_from_clientsecrets_and_code(
            'client_secrets.json', scope='', code=code)

        sub = credentials.id_token['sub']
        store = CredentialStore.get_by_id(sub)
        store.credentials = credentials.to_json()
        store.put()

    except crypt.AppIdentityError:
        return make_response('Authorization failed.', 401)

    return make_response('', 200)
