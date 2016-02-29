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

from flask import Flask, request, make_response, render_template, session
from oauth2client import client, crypt
from apiclient.discovery import build
import httplib2

from google.appengine.ext import ndb

app = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)
app.debug = True

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']

# On this sample, this is not really a secret
# Make sure to change SECRET_KEY for your own purposes
SECRET_KEY = 'abcde'
app.config.update(
    SECRET_KEY=SECRET_KEY
)


class CredentialStore(ndb.Model):
    id_token = ndb.JsonProperty()
    credentials = ndb.JsonProperty()

    @classmethod
    def remove(cls, key):
        ndb.Key(cls.__name__, key).delete()


@app.route('/')
def index():
    mode = request.args.get('mode', 'introduction')
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
    store = CredentialStore.get_by_id(sub)
    if store is None:
        # If the user doesn't exist
        store = CredentialStore(id=sub, id_token=idinfo)
    else:
        # If the user already exists
        store.id_token = idinfo

    store.put()

    session['id'] = sub

    return make_response('', 200)


@app.route('/code', methods=['POST'])
def code():
    code = request.form.get('code', '')
    credentials = client.credentials_from_clientsecrets_and_code(
        'client_secrets.json', scope='', code=code)

    if credentials is None:
        # Couldn't obtain the credential object
        return make_response('Invalid authorization code.', 401)

    sub = credentials.id_token['sub']
    store = CredentialStore.get_by_id(sub)

    if store is None:
        # id_token not stored
        return make_response('Authorization before authentication.', 401)
        # Just chose not to authenticate at the same time here because
        # Google recommendation is to separate AuthN and AuthZ.
        # But you could optionally do so if it makes sense.

    store.credentials = credentials.to_json()
    store.put()

    return make_response('', 200)
