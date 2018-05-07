import requests, re
import pandas as pd
from datetime import date, timedelta
from bs4 import BeautifulSoup

day_span = 7     # number of days in period range
num_artists = 25 # number of artists to keep track of (50 artists per page)

artist_counts = [ ]

d0 = date(2018, 1, 1) # earliest date to consider
dn = date.today()     # latest date to consider (today)
dd = timedelta(days=day_span)

d1 = d0 - dd
d2 = d0

# loop through relevant date ranges
while d1 >= d0:
    print('getting %s to %s' % (d1.isoformat(), d2.isoformat()))

    # scrape page for relevant date range
    url = "https://www.last.fm/user/ben-tanen/library/artists?from=%s&to=%s" % (d1.isoformat(), d2.isoformat())
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    # parse html into list of artist and play count per period
    artists = soup.find_all('tr', {'class': 'js-link-block'})[:num_artists]
    artist_counts += [{"name": artist.find('td', {'class': 'chartlist-name'}).find('a').decode_contents(), \
                      "count": int(re.search('[0-9]+', artist.find('span', {'class': 'countbar-bar-value-wrapper'}).decode_contents())[0]),
                      "start_date": d1.isoformat(), 
                      "end_date": d2.isoformat() \
                     } for artist in artists]

    # increment date ranges
    d1 -= dd
    d2 -= dd

# convert to dataframe and save
df = pd.DataFrame(artist_counts)
df.to_csv('data/top-artists-%ddays-%s-to-%s.csv' % (day_span, d1.isoformat(), d0.isoformat()), index = False)
