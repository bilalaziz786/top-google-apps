import six

reload(six)
import webapp2
import traceback

from google.appengine.ext.webapp import template
from requests_toolbelt.adapters import appengine
from google.appengine.api import taskqueue

from utils import *

appengine.monkeypatch()


class HomePage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("""<!doctype html>
                                    <html>        
                                    <head>
                                      <title>Top Apps</title>
                                    </head>
                                    <body>
                                        <p><a href="home" target="_blank">Go to homepage...</a></p>
                                    </body>
                                    </html>"""
                                )


class MainPage(webapp2.RequestHandler):
    def get(self):
        try:
            # Fetch the most recent apps from Cache.
            top_apps = fetch_apps_from_cache()
            if not top_apps:
                top_apps = fetch_apps_from_datastore()
                store_in_cache(top_apps)
            top_apps_temp = {'top_apps': top_apps}
            self.response.out.write(template.render('templates/index.html', top_apps_temp))
        except Exception as e:
            logger.error("Error {} occurred while rendering home page {}".format(e, traceback.print_exc()))
            self.response.set_status(500)
            self.response.out.write("Error. Please try again after some time")


class Enqueue(webapp2.RequestHandler):
    def get(self):
        try:
            task = taskqueue.add(url='/scrape', target='worker-top-apps', queue_name='top-apps-queue')
            self.response.write('Scraping Task {} enqueued, ETA {}.'.format(task.name, task.eta))
        except Exception as e:
            logger.error("Error {} occurred while enqueing {}".format(e, traceback.print_exc()))
            self.response.set_status(500)
            self.response.out.write("Error. Please try again after some time")


class GetDetails(webapp2.RequestHandler):
    def get(self):
        try:
            app_id = self.request.get('app_id')
            details = fetch_app_details(app_id)[0]
            details = {'details': details}
            self.response.out.write(template.render('templates/details.html', details))
        except Exception as e:
            logger.error("Error {} occurred while getting details {}".format(e, traceback.print_exc()))
            self.response.set_status(500)
            self.response.out.write("Error. Please try again after some time")


app = webapp2.WSGIApplication(
    [('/home', MainPage), ('/get_details', GetDetails), ('/', HomePage),
     ('/add_to_queue', Enqueue)], debug=True)

if __name__ == '__main__':
    app.run()
