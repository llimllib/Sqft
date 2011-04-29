from sqft.search.models import *
from django.core.serializers import serialize
from django.utils import simplejson
from functools import partial
from datetime import date

serialize = partial(serialize, "json")

def fixdate(rentals):
    #mysql's default date, 0000-00-00, gets translated to null by django, which then causes
    #my tests to error because available_date isn't supposed to be nullable.
    for rental in rentals:
        if not rental.available_date:
            rental.available_date = date(2009, 01, 01)
            rental.save()

def run():
    n = Neighborhood.objects.all()
    file("search/fixtures/hoods.json", "w").write(serialize(n))

    z = Zillow_Neighborhood.objects.all()
    file("search/fixtures/zillow_hoods.json", "w").write(serialize(z))

    c = Crime.objects.all().order_by('?')[0:150]
    file("search/fixtures/crimes.json", "w").write(serialize(c))

    pois = PointsOfInterest.objects.all().order_by('?')[0:150]
    file("search/fixtures/pois.json", "w").write(serialize(pois))

    parks = Park.objects.all()
    file("search/fixtures/parks.json", 'w').write(serialize(parks))

    rentals = Rental.objects.all()
    fixdate(rentals)
    file("search/fixtures/rentals.json", 'w').write(serialize(rentals))

    landlords = Landlord.objects.all()
    file("search/fixtures/landlords.json", 'w').write(serialize(landlords))

    rental_photos = RentalPhoto.objects.all()
    file("search/fixtures/rental_photos.json", 'w').write(serialize(rental_photos))

    rental_features = Feature.objects.all()
    file("search/fixtures/features.json", 'w').write(serialize(rental_features))

    poits = []
    for poi in pois:
        if len(poi.types.all()) > 0:
            poits.append(serialize(poi.types.all()).strip("[]"))
    file("search/fixtures/poi_types.json", "w").write("[%s]" % (",".join(poits)))
