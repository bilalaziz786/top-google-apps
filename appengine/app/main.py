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

import six

reload(six)
import webapp2
import play_scraper

# [START gae_python38_datastore_store_and_fetch_times]
from google.appengine.ext.webapp import template
from requests_toolbelt.adapters import appengine
from google.appengine.ext import db
from models import TopApps

appengine.monkeypatch()

from google.appengine.api import memcache



def previous_apps_in_db():
    q = db.Query(TopApps)
    # query = datastore_client.query(kind='apps')
    q.order = ['title']
    existing_apps = q.fetch(50)
    previous_apps_dict = {}
    for app in existing_apps:
        # putting False to track visited/not visited. Initially it would all be non visited i.e., False.
        app_id = app.app_id.decode('utf-8') if isinstance(app.app_id, bytes) else app.app_id
        previous_apps_dict[app_id] = [app.use, app, False]
    return previous_apps_dict


# [START gae_python38_datastore_store_and_fetch_times]
def store_apps(top_apps):
    final_list = []
    previous_apps_dict = previous_apps_in_db()
    for app in top_apps:
        if not previous_apps_dict.get(app['app_id'], [False])[0]:
            top_app = TopApps(key_name=app['app_id'])
            top_app.app_id = app['app_id']
            top_app.description = app['description']
            top_app.developer = app['developer']
            top_app.developer_id = app['developer_id']
            top_app.free = app['free']
            top_app.full_price = app['full_price']
            top_app.icon = app['icon']
            top_app.price = app['price']
            top_app.score = app['score']
            top_app.title = app['title']
            top_app.url = app['url']
            top_app.use = True
            previous_apps_dict[app['app_id']] = [True, app, True]
            final_list.append(top_app)
        else:
            previous_apps_dict[app['app_id']] = [True, app, True]
    for item in previous_apps_dict:
        if not previous_apps_dict[item][2]:
            top_app = TopApps(key_name=item)
            task = previous_apps_dict[item][1]
            top_app.app_id = task['app_id']
            top_app.description = task['description']
            top_app.developer = task['developer']
            top_app.developer_id = task['developer_id']
            top_app.free = task['free']
            top_app.full_price = task['full_price']
            top_app.icon = task['icon']
            top_app.price = task['price']
            top_app.score = task['score']
            top_app.title = task['title']
            top_app.url = task['url']
            task.use = False
            final_list.append(top_app)
    db.put(final_list)
    memcache.flush_all()


def fetch_apps_from_datastore():
    q = db.Query(TopApps)
    q.filter('use =', True)
    apps = list(q.fetch(50))

    return apps


def fetch_app_details(app_id):
    q = db.Query(TopApps)
    q.filter('app_id =', app_id)
    details = list(q.fetch(50))

    return details


def store_in_cache(apps):
    memcache.add(key="apps", value=apps, time=3600)
    print 'Successfully stored in cache'


def fetch_apps_from_cache():
    print 'Fetching from cache...'
    top_apps = memcache.get("apps")
    return top_apps


# [START gae_python38_datastore_render_times]
class MainPage(webapp2.RequestHandler):
    def get(self):
        # Fetch the most recent apps from Cache.
        top_apps = fetch_apps_from_cache()
        if not top_apps:
            top_apps = fetch_apps_from_datastore()
            store_in_cache(top_apps)
        top_apps_temp = {'top_apps': top_apps}
        self.response.out.write(template.render('templates/index.html', top_apps_temp))


class ReScrape(webapp2.RequestHandler):
    def function_to_handle_requests(self):
        top_apps = play_scraper.search('top', page=2)
        # Store the current access time in Datastore.
        store_apps(top_apps)
        top_apps_temp = {'top_apps': top_apps}
        self.response.out.write(template.render('templates/index.html', top_apps_temp))

    def get(self):
        self.function_to_handle_requests()

    def post(self):
        self.function_to_handle_requests()


class GetDetails(webapp2.RequestHandler):
    def get(self):
        app_id = self.request.get('app_id')
        details = fetch_app_details(app_id)[0]
        details = {'details': details}
        self.response.out.write(template.render('templates/details.html', details))


# [END gae_python38_datastore_render_times]

app = webapp2.WSGIApplication([('/', MainPage), ('/scrape', ReScrape), ('/get_details', GetDetails)], debug=True)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run()
