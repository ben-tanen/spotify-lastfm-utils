import requests, re
import pandas as pd
from datetime import date, timedelta
from bs4 import BeautifulSoup

day_span = 30
num_artists = 25

d0 = date.today()
dn = date(2018, 1, 1)
dd = timedelta(days=day_span)

d1 = d0 - dd
d2 = d0

artist_counts = [ ]

while d1 >= dn:
    print('getting %s to %s' % (d1.isoformat(), d2.isoformat()))

    url = "https://www.last.fm/user/ben-tanen/library/artists?from=%s&to=%s" % (d1.isoformat(), d2.isoformat())
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    artists = soup.find_all('tr', {'class': 'js-link-block'})[:num_artists]

    artist_counts += [{"name": artist.find('td', {'class': 'chartlist-name'}).find('a').decode_contents(), \
                      "count": int(re.search('[0-9]+', artist.find('span', {'class': 'countbar-bar-value-wrapper'}).decode_contents())[0]),
                      "start_date": d1.isoformat(), 
                      "end_date": d2.isoformat() \
                     } for artist in artists]

    d1 -= dd
    d2 -= dd

df = pd.DataFrame(artist_counts)
df.to_csv('data/top-artists-%ddays-%s-to-%s.csv' % (day_span, d1.isoformat(), d0.isoformat()), index = False)
