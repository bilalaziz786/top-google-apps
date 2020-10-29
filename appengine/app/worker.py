import webapp2
from utils import *
import play_scraper
from google.appengine.ext.webapp import template
from requests_toolbelt.adapters import appengine
import traceback

appengine.monkeypatch()


class ReScrape(webapp2.RequestHandler):
    def function_to_handle_requests(self):
        try:
            top_apps = play_scraper.search('game', page=2)
            # Store the current access time in Datastore.
            store_apps(top_apps)
            top_apps_temp = {'top_apps': top_apps}
            self.response.out.write(template.render('templates/index.html', top_apps_temp))
        except Exception as e:
            logger.error("Error {} occurred while scraping new apps {}".format(e, traceback.print_exc()))
            self.response.set_status(500)
            self.response.out.write("Error. Please try again after some time")

    def get(self):
        self.function_to_handle_requests()

    def post(self):
        self.function_to_handle_requests()


app = webapp2.WSGIApplication([('/scrape', ReScrape)], debug=True)
