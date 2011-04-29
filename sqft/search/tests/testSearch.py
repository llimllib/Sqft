from django.core import serializers
from django.test import TestCase
from django.utils import simplejson
from time import sleep
import re

class SearchTest(TestCase):
    fixtures = ['hoods.json', 'zillow_hoods', 'pois.json', 'poi_types.json', 'rentals.json',
                'rental_photos.json', 'landlords.json']

    def test_page_hoods_fails(self):
        #TODO: non-200 response?
        incomplete = [{'start': 10}, {'count': 2}]
        baddata = [{'start': 'a'}, {'count': 'b'}, {'start': 'a', 'count': 'b'}]

        for d in incomplete + baddata:
            try:
                r = self.client.get('/search/page_hoods', d)
                self.fail()
            except: pass

    def test_results_page(self):
        d = {'bedFloor':  u'0',
        'neighborhoods': u'',
        'bathFloor': u'0',
        'priceCeiling': u'2000',
        'priceFloor': u'700'}
        r = self.client.post('/search/results', d)
        self.assert_(r.status_code == 200)

    def test_rental_page(self):
        d = {u"id": u'1'}
        r = self.client.get('/rental', d)
        self.assert_(r.status_code == 200, "invalid rental")

    def test_rental_page_error(self):
        d = {u"id": u'abracadabra'}
        try:
            r = self.client.get('/rental', d)
            self.fail()
        except: pass

    def test_results_page_with_hoods(self):
        d = {'bedFloor':  u'0',
        'neighborhoods': u'',
        'bathFloor': u'1',
        'priceCeiling': u'2000',
        'priceFloor': u'700'}

        hoods = ["", "1", "5,12", "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15"]
        for hood in hoods:
            d['neighborhoods'] = hood
            hs = hood.split(",")
            r = self.client.post('/search/results', d)
            self.assert_(r.status_code == 200, "with %s" % hood)
            page = r.content
            self.assert_(re.findall("var rentals", page), "with %s" % hood)
            apts = simplejson.loads(re.findall('var rentals = (\[.*\])', page)[0])
            if len(hoods[0]):
                self.assert_(all(a['fields']['neighborhood'] in hs for a in apts),
                             "with %s on apts:\n%s" % (hood, apts))

    def test_json_datas(self):
        d = {'bedFloor':  u'0',
        'neighborhoods': u'',
        'bathFloor': u'1',
        'priceCeiling': u'2000',
        'priceFloor': u'700'}

        r = self.client.post('/search/results', d)
        page = r.content
        #verify that each of these variables is valid json
        for jsonlist in ["neighborhoodData", "fullHoodList", "features", "rentals"]:
            js = re.findall('var %s = ([[{].*[\]}])' % jsonlist, page)
            self.assert_(simplejson.loads(js[0]) != None, "Unable to find json for %s" % jsonlist)
            if jsonlist == "fullHoodList":
                #let's assure that the list is in alpha order. First, we only
                #care about the keys, not the arrays, so let's delete them
                all_hoods = re.sub("\[.*?\]", "", js[0])
                #then, grab all the keys
                all_hoods = re.findall(r'"(\w+)"\s*:', all_hoods)
                self.assert_(len(all_hoods))
                self.assert_(all_hoods == list(sorted(all_hoods)))

    def test_bedrooms(self):
        d = {'bedFloor':  u'0',
        'neighborhoods': u'',
        'bathFloor': u'1',
        'priceCeiling': u'2000',
        'priceFloor': u'700'}

        for bf in range(7):
            d['bedFloor'] = unicode(bf)
            r = self.client.post('/search/results', d)
            self.assert_(r.status_code == 200)
            page = r.content
            apts = re.findall('var rentals = (\[.*\])', page)
            if not apts: continue
            apts = simplejson.loads(apts[0])
            self.assert_(all(a['fields']['bedrooms'] >= bf for a in apts))

    def test_baths(self):
        d = {'bedFloor':  u'0',
        'neighborhoods': u'',
        'bathFloor': u'1',
        'priceCeiling': u'2000',
        'priceFloor': u'700'}

        for bf in range(7):
            d['bathFloor'] = unicode(bf)
            r = self.client.post('/search/results', d)
            self.assert_(r.status_code == 200)
            page = r.content
            apts = re.findall('var rentals = (\[.*\])', page)
            if not apts: continue
            apts = simplejson.loads(apts[0])
            self.assert_(all(a['fields']['full_bathrooms'] >= bf for a in apts))

    def test_prices(self):
        d = {'bedFloor':  u'0',
        'neighborhoods': u'',
        'bathFloor': u'1',
        'priceCeiling': u'2000',
        'priceFloor': u'700'}

        for low in range(0, 2000, 200):
            for high in range(0, 2000, 200):
                d['priceCeiling'] = unicode(high)
                d['priceFloor'] = unicode(low)

                r = self.client.post('/search/results', d)
                self.assert_(r.status_code == 200)
                page = r.content
                apts = re.findall('var rentals = (\[.*\])', page)
                if low > high:
                    self.assert_(not apts)
                    continue
                if not apts: continue

                apts = simplejson.loads(apts[0])
                self.assert_(all(high >= a['fields']['monthly_rent'] >= low for a in apts))
        
    def test_page_hoods(self):
        for c in [2,5,10]:
            self.assert_json('/search/page_hoods',
                             {'start':0, 'count':c},
                             expected_len=c)
        for s in [0,2,10]:
            self.assert_json('/search/page_hoods',
                             {'start':s, 'count':c},
                             expected_len=c)

    def test_search(self):
        r = self.client.get('/search/')
        self.assert_(r.status_code == 200)

    def assert_json(self, req, params={}, expected_code=200, expected_len=None):
        r = self.client.get(req, params)
        self.assert_(r.status_code == expected_code)
        data = simplejson.loads(r.content)
        if expected_len:
            self.assert_(len(data) == expected_len)
        self.assert_('application/json' in r['Content-Type'])
        return data

    def test_distance(self):
        self.assert_json('/search/distance',
                         {'address': '4137 falls rd, baltimore, md'})
        self.assert_json('/search/distance',
                         {'address': 'bad address. Bad!'},
                         expected_len=0)
    
    def test_flickr(self):
        self.assert_json('/search/hood_pics', {'hood_id': 1}, expected_len=12)

    def test_points_of_interest_with_bad_data(self):
        incomplete = [{}, {'start': 10}, {'count': 2}]
        baddata = [{'start': 'a'}, {'count': 'b'}, {'start': 'a', 'count': 'b'}]

        for d in incomplete + baddata:
            try:
                r = self.client.get('/search/points_of_interest', d)
                self.fail()
            except: pass

    def test_points_of_interest(self):
        for c in [0,2,5]:
            self.assert_json('/search/points_of_interest',
                             {"start": 0, "count": c},
                             expected_len=c)

        for s in [0,2,5]:
            self.assert_json('/search/points_of_interest',
                             {"start": s, "count": c},
                             expected_len=c)
