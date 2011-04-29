from django.core import serializers
from django.test import TestCase
from django.utils import simplejson
from sqft.utils.decodegmap import encode_points, decode_points
from sqft.search.models import Park 
from StringIO import StringIO

class ParkModelTest(TestCase):
    fixtures = ['parks.json']

    def test_valid_name(self):
        s = StringIO()
        for p in Park.objects.all():
            #if p.__unicode__ fails, this will throw
            s.write(p)
        s.close()

    def test_border_valid(self):
        for park in Park.objects.all():
            #decode_points should fail on an invalid border
            len(decode_points(park.encodedBorder))
