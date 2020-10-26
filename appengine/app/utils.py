from google.appengine.api import memcache
from google.appengine.ext import db
from models import TopApps
import logging

logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)


def previous_apps_in_db():
    q = db.Query(TopApps)
    q.order = ['title']
    existing_apps = q.fetch(50)
    previous_apps_dict = {}
    for app in existing_apps:
        # putting False to track visited/not visited. Initially it would all be non visited i.e., False.
        app_id = app.app_id.decode('utf-8') if isinstance(app.app_id, bytes) else app.app_id
        previous_apps_dict[app_id] = [app.use, app, False]
    return previous_apps_dict


def store_apps(top_apps):
    final_list = []
    previous_apps_dict = previous_apps_in_db()
    for app in top_apps:
        if not previous_apps_dict.get(app['app_id'], [False])[0]:
            top_app = TopApps(key_name=app['app_id'])
            top_app = prepare_data(top_app, app)
            top_app.use = True
            previous_apps_dict[app['app_id']] = [True, app, True]
            final_list.append(top_app)
        else:
            previous_apps_dict[app['app_id']] = [True, app, True]
    for item in previous_apps_dict:
        if not previous_apps_dict[item][2]:
            top_app = TopApps(key_name=item)
            task = previous_apps_dict[item][1]
            top_app = prepare_data(top_app, task)
            top_app.use = False
            final_list.append(top_app)
    db.put(final_list)
    memcache.flush_all()


def prepare_data(top_app, app):
    top_app.app_id = app['app_id'] if isinstance(app, dict) else app.app_id
    top_app.description = app['description'] if isinstance(app, dict) else app.description
    top_app.developer = app['developer'] if isinstance(app, dict) else app.developer
    top_app.developer_id = app['developer_id'] if isinstance(app, dict) else app.developer_id
    top_app.free = app['free'] if isinstance(app, dict) else app.free
    top_app.full_price = app['full_price'] if isinstance(app, dict) else app.full_price
    top_app.icon = app['icon'] if isinstance(app, dict) else app.icon
    top_app.price = app['price'] if isinstance(app, dict) else app.price
    top_app.score = app['score'] if isinstance(app, dict) else app.score
    top_app.title = app['title'] if isinstance(app, dict) else app.title
    top_app.url = app['url'] if isinstance(app, dict) else app.url
    return top_app


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
    try:
        memcache.add(key="apps", value=apps, time=3600)
        logger.info('Successfully stored in cache')
    except Exception as e:
        logger.error("Error {} occurred while pushing in Cache".format(e))


def fetch_apps_from_cache():
    top_apps = None
    try:
        logger.info('Fetching from cache...')
        top_apps = memcache.get("apps")
    except Exception as e:
        logger.error("Error {} occurred while fetching from Cache".format(e))
    return top_apps
