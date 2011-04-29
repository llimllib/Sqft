from django.core import serializers
from django.test import TestCase
from sqft.search.models import Rental

class RentalModelTest(TestCase):
    fixtures = ['rentals.json', 'hoods.json', 'landlords.json', 'features.json',
                'rental_photos.json']

    def test_fixture_exists(self):
        self.assert_(len(Rental.objects.all()) > 5)

    def test_rental_load(self):
        for c in Rental.objects.all():
            #converting to a string is a super-basic test that all
            #fields can be accessed and exist
            s = str(c)

    def test_rental_derived_fields(self):
        rentals = Rental.objects.all()
        self.assert_(all(r.cost_per_sqft > 0 for r in rentals),
                     "invalid cost per sqft")
        self.assert_(all(r.estimated_total_cost > 0 for r in rentals),
                     "invalid estimated total cost")
        self.assert_(all(r.estimated_cost_per_sqft > 0 for r in rentals),
                     "invalid estimated cost per sqft")

    def test_rental_foreign_keys(self):
        rentals = Rental.objects.all()
        self.assert_(all(r.neighborhood for r in rentals),
                     "accessing hood raised error")
        self.assert_(all(r.landlord for r in rentals),
                     "accessing landlord raised error")
        try:
            #we simply expect the features array to work, not necessarily to contain anything
            [r.features for r in rentals]
        except:
            self.fail()
