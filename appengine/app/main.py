# Copyright 2018 Google LLC
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

import justext
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import datetime

from flask import Flask, render_template
from constants import *
import play_scraper

# [START gae_python38_datastore_store_and_fetch_times]
from google.cloud import datastore

datastore_client = datastore.Client()

# def requests_retry_session(retries=MAX_RETRY_FOR_SESSION,
#                            back_off_factor=BACK_OFF_FACTOR,
#                            status_force_list=ERROR_CODES):
#     session = requests.Session()
#     retry = Retry(total=retries, read=retries, connect=retries,
#                   backoff_factor=back_off_factor,
#                   status_forcelist=status_force_list,
#                   method_whitelist=frozenset(['GET', 'POST']))
#     adapter = HTTPAdapter(max_retries=retry)
#     session.mount('http://', adapter)
#     session.mount('https://', adapter)
#     return session


# [END gae_python38_datastore_store_and_fetch_times]
app = Flask(__name__)


# [START gae_python38_datastore_store_and_fetch_times]
def store_time(top_apps):
    final_list = []
    for app in top_apps:
        key = datastore_client.key('apps', app['app_id'])
        entity = datastore.Entity(key=key)
        entity.update(app)
        final_list.append(entity)
    datastore_client.put_multi(final_list)


def fetch_times():
    query = datastore_client.query(kind='apps')
    query.order = ['title']

    times = query.fetch()

    return times


def fetch_app_details(app_id):
    query = datastore_client.query(kind='apps')
    query.add_filter('app_id', '=', app_id)
    details = list(query.fetch())

    return details


# [END gae_python38_datastore_store_and_fetch_times]


# [START gae_python38_datastore_render_times]
@app.route('/')
def root():
    # top_apps = play_scraper.search('top', page=2)
    # Store the current access time in Datastore.
    # store_time(top_apps)
    # Fetch the most recent 10 access times from Datastore.
    top_apps = fetch_times()
    return render_template(
        'index.html', top_apps=top_apps)


@app.route('/scrape', methods=['POST'])
def re_scrape():
    top_apps = play_scraper.search('top', page=2)
    # Store the current access time in Datastore.
    store_time(top_apps)
    # Fetch the most recent 10 access times from Datastore.
    return render_template(
        'index.html', top_apps=top_apps)


@app.route('/get_details/<app_id>')
def get_app_details(app_id):
    details = fetch_app_details(app_id)[0]
    return render_template('details.html', details=details)


# [END gae_python38_datastore_render_times]


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
