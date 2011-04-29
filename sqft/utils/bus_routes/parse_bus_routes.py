from sqft.search.models import TransitStop, Neighborhood
from sqft.utils.geopy.geocoders import Google, Yahoo
from csv import reader, writer
from time import sleep
from os.path import dirname, join
from functools import partial
from utils.crime.crime_locate import is_in
import logging

selfdir = partial(join, dirname(__file__))

logging.getLogger().setLevel(logging.CRITICAL)

#g = Google('ABQIAAAAi38qWc-9V8q5b6bgPClsfxTfKEWMeMOdp19wa3uONsY3R1LXvRTgTR8o6snPUFoi7M-AG31rpq6VWQ')
g = Yahoo('bKVpVX_V34Ec62VfSmdXD1Sow.dHyfSQfxCp5qeug95VuX1.mxPFUZvqYDR1HUb8WOyE.d.q')
def geocode(addr):
    gc = list(g.geocode(addr, False))
    if not len(gc):
        print "sleeping for 2..."
        sleep(2)
        gc = list(g.geocode(addr, False))
        if not len(gc):
            return None
    #we only want the best result
    gc = gc[0]
    if type(gc[0]) != type(u''):
        print gc, " is not what I was expecting"
        raise Exception("wtf duder %s" % addr)
    return (gc[0], gc[1])

def run_geocode():
    r = reader(open(selfdir('bus_routes.csv')))
    #skip the headers
    r.next()
    i = iter(r)
    for route in i:
        mode, name = route[:2]
        name = name.split('-')[0].strip()
        stops = route[2:]
        for stop in stops:
            stop += ", baltimore, md"
            gc = geocode(stop)
            if not gc:
                print "unable to find %s" % stop
                continue
            addr, (lat, lon) = gc
            b = TransitStop(transit_type=mode, address=addr, latitude=lat, longitude=lon, route=name)
            b.save()
        #throw away every other row
        i.next()

def find_neighborhoods():
    hoods = Neighborhood.objects.all()
    for bs in TransitStop.objects.all():
        for hood in hoods:
            if is_in((bs.latitude, bs.longitude), hood.border):
                bs.neighborhood = hood
                bs.save()
                break

def rate_hoods():
    stops = []
    for hood in Neighborhood.objects.all():
        stops.append((len(TransitStop.objects.filter(neighborhood=hood)), hood))
    max_stops = max(stops)[0]
    for stops, hood in stops:
        hood.transit_rating = (float(stops)/max_stops) ** (1/8.)
        hood.save()

def run():
    #run_geocode()
    #find_neighborhoods()
    #rate_hoods()

if __name__ == "__main__": run()
