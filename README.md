Website that lets user browse top android apps. The website will contain two pages - landing page and a detail page. Please see Specs section below for UI details

On the landing page user will see a list of all top android apps. These apps are scraped from Google Play Store: https://play.google.com/store/apps/top and stored in website’s DB.

The apps will be showed landing page by fetching from DB.

The landing page contains a button that will re-scrape all the data from the top apps page and update the entries in the DB. If new apps are available, we add them to our db, but do not delete the apps that have already been scraped but removed from the top apps page.

On clicking any app on the landing page of the website, user will be redirected to the detail page of our website where more information about the app will be shown.