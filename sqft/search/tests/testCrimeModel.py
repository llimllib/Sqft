from django.core import serializers
from django.test import TestCase
from sqft.search.models import Crime 

class CrimeModelTest(TestCase):
    fixtures = ['crimes.json']

    def test_fixture_exists(self):
        self.assert_(len(Crime.objects.all()) > 10)

    def test_crime_load(self):
        for c in Crime.objects.all():
            #converting to a string is a super-basic test that all
            #fields can be accessed and exist
            s = str(c)
