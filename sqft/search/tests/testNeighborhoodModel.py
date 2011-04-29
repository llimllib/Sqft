from django.core import serializers
from django.test import TestCase
from django.utils import simplejson
from sqft.utils.decodegmap import encode_points, decode_pairs
from sqft.search.models import Neighborhood

class NeighborhoodModelTest(TestCase):
    fixtures = ['hoods.json']

    def test_hoods_exist(self):
        self.assert_(len(Neighborhood.objects.all()) > 10)
    
    def test_border(self):
        for hood in Neighborhood.objects.all():
            self.assert_(decode_pairs(hood.encodedBorder) == hood.border)
