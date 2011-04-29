from time import mktime
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core import serializers
from django.views.generic.list_detail import object_list
from django.utils import simplejson
from sqft.search.models import Rental, Neighborhood, Crime, Feature, Zillow_Neighborhood, PointsOfInterest, PointsOfInterestTypes, TransitStop, Park, School, Market
import random
from collections import defaultdict
from datetime import datetime
from django.conf import settings
from sqft.utils import flickrapi
from sqft.utils.geopy.distance import distance
from sqft.utils.geopy.geocoders import Google as GoogleGeocode

GMAPS_API_KEY = settings.GMAPS_API_KEY
GEOCODE = GoogleGeocode(GMAPS_API_KEY).geocode
PAGE_SIZE = 20

def results(request):
    apts = Rental.objects.filter(
        bedrooms__gte=request.POST['bedFloor'],
        full_bathrooms__gte=request.POST['bathFloor'],
        monthly_rent__gte=request.POST['priceFloor'],
        monthly_rent__lte=request.POST['priceCeiling'])
    if len(request.POST['neighborhoods']) > 0:
        apts = apts.filter(neighborhood__in=request.POST['neighborhoods'].split(","))
        
    aptsjson = serializers.serialize("json", apts)

    hood_groups = {}
    for apt in apts:
        hood = apt.neighborhood.name
        center = apt.neighborhood.center_point
        hood_groups.setdefault(hood, [center]).append(apt)
    
    hoods = Neighborhood.objects.all()

    hood_data = []
    for hood in hoods[:PAGE_SIZE]:
        hood = _serialize(hood)
        hood_data.append(hood)

    feature_data = {}
    for f in Feature.objects.all():
        feature_data.setdefault(f.room, []).append({'feature_id': f.pk, 'name': f.name})

    
    return object_list(request,
                       template_name        = 'results.html',
                       queryset             = apts,
                       template_object_name = 'rentals',
                       extra_context        = {'aptsjson':  aptsjson,
                                               'hood_apts': hood_groups,
                                               'hood_names': _get_hood_groups(),
                                               'hood_data': simplejson.dumps(hood_data),
                                               'features': simplejson.dumps(feature_data),
                                               'search_request': request.POST, 
                                               'gmaps_key': GMAPS_API_KEY})

#a very simple serialization
def _serialize(model_instance):
    #the defaultdict returns an identity function by default
    types = defaultdict(lambda: lambda x: x)
    types[datetime] = lambda x: unicode(x)

    r = {}
    for f in model_instance._meta.fields:
        attval = getattr(model_instance, f.attname)
        #serialize the type if it needs serialization
        attval = types[attval.__class__](attval)
        r[f.attname] = attval
    return r

def search(request):
    hoods = Neighborhood.objects.all()

    hood_data = []
    for hood in hoods[:PAGE_SIZE]:
        hood = _serialize(hood)
        hood_data.append(hood)

    feature_data = {}
    for f in Feature.objects.all():
        feature_data.setdefault(f.room, []).append({'feature_id': f.pk, 'name': f.name})

    return render_to_response("search.html",
                                {'hood_names': _get_hood_groups(),
                                 'hood_data': simplejson.dumps(hood_data),
                                 'features': simplejson.dumps(feature_data),
                                 'gmaps_key': GMAPS_API_KEY})

def rental(request):
    rental = Rental.objects.get(rental_id=int(request.GET['id']))
    apt = Rental.objects.filter(rental_id__exact=int(request.GET['id']))
    aptjson = serializers.serialize("json", apt)
    features = {"Water": rental.water_included,
                "Parking": not rental.parking_cost,
                "Electric": rental.utilities_included,
                "Heat": rental.heat_included,
                "Cable": rental.cable_provided,
                "Internet": rental.internet_provided,
                "Phone": rental.phone_provided}
    
    #XXX: this will end up being something we want to calculate ahead of time
    in_hood = Rental.objects.filter(neighborhood=rental.neighborhood, bedrooms=rental.bedrooms)
    cost_pct = [r.estimated_total_cost for r in in_hood]
    cost_pct.sort()
    l = float(len(cost_pct))
    idx = cost_pct.index(rental.estimated_total_cost)
    if l == 1: cost_pct = 50
    else:      cost_pct = int(((l-idx-1)/(l-1)) * 100)

    cost_sqft = [r.estimated_cost_per_sqft for r in in_hood]
    cost_sqft.sort()
    l = float(len(cost_sqft))
    idx = cost_sqft.index(rental.estimated_cost_per_sqft)
    if l == 1: cost_sqft = 50
    else:      cost_sqft = int(((l-idx-1)/(l-1)) * 100)

    return render_to_response("rental.html",
                                {'rental': rental,
                                 'aptjson': aptjson,
                                 'features': features,
                                 'cost_pct': cost_pct,
                                 'cost_sqft': cost_sqft,
                                 'gmaps_key': GMAPS_API_KEY})
    

#return "count" neighborhoods from start in JSON
def page_hoods(request):
    start = int(request.GET['start'])
    end = start + int(request.GET['count'])

    hoods = Neighborhood.objects.all()[start:end]
    hood_data = []
    for hood in hoods[:20]:
        hood = _serialize(hood)
        hood_data.append(hood)
    return HttpResponse(simplejson.dumps(hood_data), mimetype='application/json')

#return the distance between an address and each neighborhood, if the address
#is found - else return an empty array
def distance_from_address(request):
    #first, geocode the address
    addr = request.GET['address']
    #TODO: I should be able to build my own geocoding database from the 
    #      TIGER data. until then, this will fail if hit too often plus
    #      it may fail if hit some amount of times during a day
    gc = list(GEOCODE(addr, False))
    if not len(gc):
        return HttpResponse("[]", mimetype='application/json')
    else:
        addr, latlon = gc[0]
        ds = sorted((distance(n.center_point, latlon).miles, n.name, n.pk)
                    for n in Neighborhood.objects.all())
        return HttpResponse(simplejson.dumps(ds), mimetype='application/json')

#return neighborhood groups in the format
#{"group name": [{"name": neighborhood.name,
#                 "neighborhood_id": neighborhood.pk}...],
# "group 2":    [{...}, {...}], 
# ...}
def _get_hood_groups():
    groups = {}
    for hood in Neighborhood.objects.all():
        zh = hood.zillow_neighborhood.name
        if zh in groups:
            groups[zh].append({'name': hood.name,
                               'neighborhood_id': hood.neighborhood_id})
        else:
            groups[zh] = [{'name': hood.name,
                           'neighborhood_id': hood.neighborhood_id}]
    #john resig says that I can rely on javascript object sorting:
    # http://ejohn.org/blog/javascript-in-chrome/
    # so I'll make it happen in a super hacky way, because simplejson expects
    # (reasonably) that objects don't have an order. Hack the planet!
    dumps = simplejson.dumps
    return '{%s}' % ','.join(("%s: %s" % tuple(map(dumps, (k,v)))
                              for k,v in sorted(groups.iteritems())))

def points_of_interest(request):
    start = int(request.GET['start'])
    end = start + int(request.GET['count'])
    if 'type' in request.GET:
        type = request.GET['type']
        ps = PointsOfInterest.objects.filter(types__type__exact=type)[start:end]
    else:
        ps = PointsOfInterest.objects.all()[start:end]

    pp = []
    for p in ps:
        q = _serialize(p)
        q.update({'type': [t.type for t in p.types.all()]})
        pp.append(q)
    return HttpResponse(simplejson.dumps(pp), mimetype='application/json')

def get_flickr_pics(request):
    hood = Neighborhood.objects.get(pk=int(request.GET['hood_id']))
    f = flickrapi.FlickrAPI(settings.FLICKR_API_KEY)
    r = f.photos_search(woe_id=hood.flickr_woeid,
        min_upload_date=mktime((datetime.today()-timedelta(120)).timetuple()),
        sort='interestingness-desc',
        per_page=12)
    httemplate = "http://farm%(farm)s.static.flickr.com/%(server)s/%(id)s_%(secret)s_m.jpg"
    links = []
    for photo in r.getchildren()[0]:
        links.append(httemplate % photo.attrib)
    return HttpResponse(simplejson.dumps(links), mimetype='application/json')
