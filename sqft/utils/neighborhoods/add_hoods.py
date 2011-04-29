from csv import reader, writer
from os.path import dirname, join
from functools import partial
from sqft.search.models import Neighborhood

selfdir = partial(join, dirname(__file__))

r = reader(open(selfdir('new_hoods.csv')))
#skip the headers
r.next()
for name, border, levels in r:
    n = Neighborhood(name=name, encodedBorder=border, encodedLevels=levels,
        area=-1, color="000000", description='', crime_rating=0, restaurant_rating=0,
        nightlife_rating=0, flickr_woeid=0, zillow_neighborhood=0, transit_rating=0,
        park_rating=0, school_rating=0, market_rating=0, city_id=1)
    n.save()
