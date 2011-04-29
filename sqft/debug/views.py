from collections import defaultdict
from datetime import datetime
from django.conf import settings
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render_to_response

from sqft.search.models import Rental, Neighborhood, Crime, Feature, Zillow_Neighborhood, PointsOfInterest, PointsOfInterestTypes, TransitStop, Park, School, Market

GMAPS_API_KEY = settings.GMAPS_API_KEY

### BEGIN DEBUG VIEWS
###
### These should all be removed when we go to production, or at least
### login-required. They are untested because they are debug views!

def debug_map(request):
    return render_to_response("debug.html", {"gmaps_key": GMAPS_API_KEY})

#return 100 random crimes that are in a neighborhood
def crimes(request):
    nullcrimes = [[c.latitude, c.longitude, c.neighborhood.name + unicode(c.crime_id)]
                   for c in Crime.objects.filter(neighborhood__isnull=False).order_by('?')[:100]]
    nullcrimes = simplejson.dumps(nullcrimes)
    return HttpResponse(nullcrimes, mimetype='application/json')

def hoods(request):
    hoods = [[n.name, n.encodedBorder, n.encodedLevels, n.crime_rating]
             for n in Neighborhood.objects.all()]
    hoods = simplejson.dumps(hoods)
    return HttpResponse(hoods, mimetype='application/json')

def zillow_hoods(request):
    zhoods = [[hood.name, hood.encodedBorder, hood.encodedLevels]
               for hood in Zillow_Neighborhood.objects.all()]
    zhoods = simplejson.dumps(zhoods)
    return HttpResponse(zhoods, mimetype='application/json')

def transit_stops(request):
    return HttpResponse(simplejson.dumps(
        [[stop.route, stop.latitude, stop.longitude]
          for stop in TransitStop.objects.all()]),
        mimetype='application/json')

def parks(request):
    return HttpResponse(simplejson.dumps(
        [[park.name, park.encodedBorder, park.encodedLevels]
          for park in Park.objects.all()]),
        mimetype='application/json')

def centers(request):
    return HttpResponse(simplejson.dumps(
        [n.center_point for n in Neighborhood.objects.all()]),
        mimetype='application/json')

def schools(request):
    return HttpResponse(simplejson.dumps(
        [(s.name, s.latitude, s.longitude) for s in School.objects.all()]),
        mimetype='application/json')

def markets(request):
    return HttpResponse(simplejson.dumps(
        [(m.name, m.latitude, m.longitude) for m in Market.objects.all()]),
        mimetype='application/json')

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

def grades(request):
    hoods = [_serialize(hood) for hood in Neighborhood.objects.all()]
    return render_to_response("grades.html", {'hoods': simplejson.dumps(hoods)});
