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

import os

os.environ["DATASTORE_DATASET"] = "top-gle-apps"
os.environ["DATASTORE_EMULATOR_HOST"] = "127.0.0.1:8081"
os.environ["DATASTORE_EMULATOR_HOST_PATH"] = "127.0.0.1:8081/datastore"
os.environ["DATASTORE_HOST"] = "http://127.0.0.1:8081"
os.environ["DATASTORE_PROJECT_ID"] = "top-gle-apps"

import six
reload(six)
import webapp2
import play_scraper

# [START gae_python38_datastore_store_and_fetch_times]
from google.cloud import datastore
from google.appengine.ext.webapp import template

from google.appengine.api import memcache


datastore_client = datastore.Client()


# app = Flask(__name__)


def previous_apps_in_db():
    query = datastore_client.query(kind='apps')
    query.order = ['title']
    existing_apps = query.fetch()
    previous_apps_dict = {}
    for app in existing_apps:
        # putting False to track visited/not visited. Initially it would all be non visited i.e., False.
        app_id = app['app_id'].decode('utf-8') if isinstance(app['app_id'], bytes) else app['app_id']
        previous_apps_dict[app_id] = [app['use'], app, False]
    return previous_apps_dict


# [START gae_python38_datastore_store_and_fetch_times]
def store_apps(top_apps):
    final_list = []
    previous_apps_dict = previous_apps_in_db()
    for app in top_apps:
        if not previous_apps_dict.get(app['app_id'], [False])[0]:
            key = datastore_client.key('apps', app['app_id'])
            entity = datastore.Entity(key=key)
            app['use'] = True
            previous_apps_dict[app['app_id']] = [True, app, True]
            entity.update(app)
            final_list.append(entity)
        else:
            previous_apps_dict[app['app_id']] = [True, app, True]
    for item in previous_apps_dict:
        if not previous_apps_dict[item][2]:
            key = datastore_client.key('apps', item)
            entity = datastore.Entity(key=key)
            task = previous_apps_dict[item][1]
            task['use'] = False
            entity.update(task)
            final_list.append(entity)
    datastore_client.put_multi(final_list)
    # memcache.flush_all()


def fetch_apps_from_datastore():
    query = datastore_client.query(kind='apps')
    query.add_filter('use', '=', True)

    apps = list(query.fetch())

    return apps


def fetch_app_details(app_id):
    query = datastore_client.query(kind='apps')
    query.add_filter('app_id', '=', app_id)
    details = list(query.fetch())

    return details


def store_in_cache(apps):
    memcache.add(key="apps", value=apps, time=3600)
    print("Successfully stored in cache")


def fetch_apps_from_cache():
    print("Fetching from cache...")
    top_apps = memcache.get("apps")
    return top_apps


# [START gae_python38_datastore_render_times]
class MainPage(webapp2.RequestHandler):
    def get(self):
        # Fetch the most recent apps from Cache.
        # top_apps = fetch_apps_from_cache()
        top_apps = None
        if not top_apps:
            top_apps = fetch_apps_from_datastore()
            # store_in_cache(top_apps)
        # return render_template(
        #     'index.html', top_apps=top_apps)
        top_apps_temp = {'top_apps': top_apps}
        self.response.out.write(template.render('templates/index.html', top_apps_temp))


class ReScrape(webapp2.RequestHandler):
    def post(self):
        top_apps = play_scraper.search('top', page=2)
        # Store the current access time in Datastore.
        store_apps(top_apps)
        # Fetch the most recent 10 access times from Datastore.
        # return render_template(
        #     'index.html', top_apps=top_apps)
        top_apps_temp = {'details': top_apps}
        self.response.out.write(template.render('index.html', top_apps_temp))


# @app.route('/get_details/<app_id>')
# def get_app_details(app_id):
#     details = fetch_app_details(app_id)[0]
#     return render_template('details.html', details=details)


# [END gae_python38_datastore_render_times]

app = webapp2.WSGIApplication([('/', MainPage), ('/scrape', ReScrape)], debug=True)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run()
