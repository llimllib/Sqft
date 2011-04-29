from csv import reader, writer
from os.path import dirname, join
from functools import partial
from time import sleep
from sqft.utils.geopy.geocoders import Google
from sqft.utils.geopy.distance import distance
from sqft.utils.decodegmap import decode_pairs
from sqft.search.models import Market, Neighborhood
from utils.crime.crime_locate import is_in

selfdir = partial(join, dirname(__file__))

g = Google('ABQIAAAAi38qWc-9V8q5b6bgPClsfxTfKEWMeMOdp19wa3uONsY3R1LXvRTgTR8o6snPUFoi7M-AG31rpq6VWQ')
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

def parse_csv():
    r = reader(open(selfdir('supermarkets.csv')))
    #skip the headers
    r.next()
    for market, addr in r:
        gc = geocode(addr + " baltimore, md")
        if not gc:
            print "couldn't find %s" % addr
            continue
        addr, (lat, lon) = gc
        m = Market(name=market, address=addr, latitude=lat, longitude=lon)
        m.save()

def get_hood():
    hoods = Neighborhood.objects.all()
    for market in Market.objects.all():
        for hood in hoods:
            if is_in((market.latitude, market.longitude), hood.border):
                market.neighborhood = hood
                market.save()
                break

def score_hood():
    #we should probably take distance into account if the hood has no market
    #example: medfield gets a bad rating even though Superfresh is across the
    #street
    hoods = []
    for hood in Neighborhood.objects.all():
        if len(hood.market_set.all()) > 0:
            hood.market_rating = 1
            hood.save()
        else:
            #find the distance to the closest market from each border point
            mind = min(distance((m.latitude, m.longitude), ll).meters
                       for m in Market.objects.all()
                       for ll in hood.border)
            hoods.append((mind, hood))
    maxd = float(max(hoods)[0])
    hoods = [(maxd-d, hood) for d, hood in hoods]
    maxd = max(hoods)[0]
    for d, hood in hoods:
        #multiply these hoods by .75 because they shouldn't beat the hoods
        #that actually have markets in them
        hood.market_rating = (d/maxd)*.75
        hood.save()

def run():
    #parse_csv()
    get_hood()
    score_hood()

if __name__=="__main__": run()
