import settings
from xml.etree.ElementTree import dump
from time import mktime
from datetime import datetime, timedelta
from sqft.search.models import Neighborhood
from sqft.utils import flickrapi

#interesting: <neighbourhood place_id="a8ZPGKSbCJ6PdxdoNw" woeid="29229393">Charles North</neighbourhood>
#shall I used the place_id and woeid args?

f = flickrapi.FlickrAPI(settings.FLICKR_API_KEY)

def run():
    for h in Neighborhood.objects.all():
        if h.flickr_woeid: continue

        lo1, la1, lo2, la2 = h.bounding_box
        clo = (lo1 + lo2) / 2
        cla = (la1 + la2) / 2
        #r = f.photos_search(lat=cla, lon=clo, radius='1', radius_units='km',
        #    min_upload_date=mktime((datetime.today()-timedelta(60)).timetuple()),
        #    per_page=1)
        #photos = r.getchildren()[0]

        #print h.name, photos.attrib['total']
        #if not photos.attrib['total']: print "couldn't find photos for %s" % h.name

        #pid = photos.getchildren()[0].attrib['id']
        #g = f.photos_geo_getLocation(photo_id=pid)
        #import pdb; pdb.set_trace()
        #return g

        #flickr doesn't seem to believe in Harbor east; it gets returned
        #as Little Italy
        r = f.places_findByLatLon(lat=cla, lon=clo, accuracy=12)

        h.flickr_woeid = r.getchildren()[0].getchildren()[0].attrib['woeid']
        h.save()
        

#application id for geoplanet, so I can look up woeids:
#jr33RvPV34Gcbbl7tq.SP3Geez7_fxQm8oXPAblUuct0y.YjnWeX2xviR2Zm045QaSJoYA5X
