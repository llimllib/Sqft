from django.db import models
from sqft.utils.decodegmap import encode_points, decode_pairs

#django wants to use longtext instead of text. kill it.
class NormalTextField(models.Field):        
    def db_type(self):
        return 'text'

class TinyTextField(models.Field):        
    def db_type(self):
        return 'tinytext'

# Create your models here.
class Neighborhood(models.Model):
    neighborhood_id = models.AutoField(primary_key=True, db_column='neighborhood_id')
    name = models.CharField(max_length=128)
    encodedBorder = NormalTextField()
    encodedLevels = models.CharField(max_length=256)
    color = models.CharField(max_length=6)
    description = NormalTextField()
    area = models.FloatField()
    crime_rating = models.FloatField()
    restaurant_rating = models.FloatField()
    nightlife_rating = models.FloatField()
    flickr_woeid = models.IntegerField()
    zillow_neighborhood = models.ForeignKey('Zillow_Neighborhood')
    transit_rating = models.FloatField()
    park_rating = models.FloatField()
    school_rating = models.FloatField()
    market_rating = models.FloatField()

    restaurant_grade = models.CharField(max_length=1)
    crime_grade = models.CharField(max_length=1)
    nightlife_grade = models.CharField(max_length=1)
    transit_grade = models.CharField(max_length=1)
    park_grade = models.CharField(max_length=1)
    school_grade = models.CharField(max_length=1)
    market_grade = models.CharField(max_length=1)
    fitness_grade = models.CharField(max_length=1)
    #XXX: steve references a services grade. What is that supposed to be?

    #TODO: need a city model
    #city_id = models.ForeignKey(City)
    #FIXME:
    city_id = models.IntegerField()

    def __unicode__(self):
        return self.name

    #unencoded border property
    def _get_border(self):
        return decode_pairs(self.encodedBorder)

    #I don't need to do this for now, I'm not going to spend time testing
    #it.
    #def _set_border(self, border):
    #    self.encodedBorder = encode_points(border)

    border = property(_get_border)

    def _get_bounding_box(self):
        points = decode_pairs(self.encodedBorder)
        p = points.pop()
        minlat = maxlat = p[0]
        minlong = maxlong = p[1]
        for lat, long in points:
            if lat < minlat: minlat = lat
            if lat > maxlat: maxlat = lat
            if long < minlong: minlong = long
            if long > maxlong: maxlong = long
        return [minlong, minlat, maxlong, maxlat]

    bounding_box = property(_get_bounding_box)

    def _get_center_point(self):
        if hasattr(self, "_center_point"): return self._center_point
        a,b,c,d = self._get_bounding_box()
        #return lat, long
        self._center_point = ((b+d)/2, (a+c)/2)
        return self._center_point

    center_point = property(_get_center_point)

    class Meta:
        db_table = 'neighborhoods'
        ordering = ['name']

class Landlord(models.Model):
    landlord_id = models.AutoField(primary_key=True, db_column='landlord_id')
    firstname = models.CharField(max_length=1024)
    lastname = models.CharField(max_length=1024)
    address1 = models.CharField(max_length=1024)
    address2 = models.CharField(max_length=1024, blank=True)
    city = models.CharField(max_length=1024)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)
    country = models.CharField(max_length=2)
    
    def __unicode__(self):
        return self.firstname + " " + self.lastname

    class Meta:
        db_table = 'landlords'

class Rental(models.Model):
    rental_id = models.AutoField(primary_key=True, db_column='rental_id')
    year_built = models.IntegerField()
    type = models.CharField(max_length=100)
    lease_terms = models.CharField(max_length=100, null=True)
    lease_description = TinyTextField(blank=True)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)
    country = models.CharField(max_length=2)
    #TODO: if the lat/long are blank, geolocate them by the address
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = NormalTextField(null=True)

    #XXX: shouldn't the following all be Features?
    #XXX: should monthly_rent be a float?
    monthly_rent = models.IntegerField()
    square_footage = models.IntegerField()
    bedrooms = models.IntegerField()
    full_bathrooms = models.IntegerField()
    half_bathrooms = models.IntegerField()
    available_date = models.DateField()
    dogs_ok = models.BooleanField()
    cats_ok = models.BooleanField()
    #TO ADD:
    cable_provided = models.BooleanField()
    phone_provided = models.BooleanField()
    internet_provided = models.BooleanField()
    parking_cost = models.IntegerField() #XXX: eventually, calc from hood?
    has_gas = models.BooleanField() #XXX: ok to assume electric otherwise?
    utilities_included = models.BooleanField()
    water_included = models.BooleanField()
    heat_included = models.BooleanField()
    has_laundry = models.BooleanField()
    has_pool = models.BooleanField()

    #foreign keys
    #XXX: neighborhood should be derived from lat/long on a new Rental, maybe?
    neighborhood = models.ForeignKey(Neighborhood)
    landlord = models.ForeignKey(Landlord)
    features = models.ManyToManyField("Feature", db_table="rental_features")

    def __unicode__(self):
        return self.address1

    class Meta:
        db_table = 'rentals'

    def firstphotourl(self, default=u"/public/photos/house_thumb.jpg"):
        p = self.rentalphoto_set.order_by('photo')
        return p[0].url if p else default

    first_photo_url = property(firstphotourl)

    def _get_rent_per_sqft(self):
       return round(float(self.monthly_rent)/float(self.square_footage), 2)

    cost_per_sqft = property(_get_rent_per_sqft)

    def _get_estimated_total_cost(self):
        etc = self.monthly_rent
        #TODO: cost of gas versus electric?
        if not self.utilities_included: etc += (.10 * self.square_footage)
        if not self.water_included: etc += 10
        if not self.cable_provided: etc += 33
        if not self.phone_provided: etc += 33
        if not self.internet_provided: etc += 33
        if not self.has_laundry: etc += 15
        return int(etc)

    estimated_total_cost = property(_get_estimated_total_cost)

    def _get_estimated_cost_per_sqft(self):
        return round(self.estimated_total_cost / float(self.square_footage), 2)

    estimated_cost_per_sqft = property(_get_estimated_cost_per_sqft)

class RentalPhoto(models.Model):
    photo = models.AutoField(primary_key=True, db_column='photo_id')
    url = models.CharField(max_length=255) #XXX: is that long enough?
    ordering = models.IntegerField()

    #foreign keys
    rental = models.ForeignKey(Rental)

    def __unicode__(self):
        return self.url

    class Meta:
        db_table = 'rental_photos'

class Crime(models.Model):
    crime_id = models.AutoField(primary_key=True, db_column='crime_id')
    case_number = models.CharField(max_length=25)
    crime = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    reported_on = models.DateTimeField()
    #TODO: better name?
    type = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    neighborhood = models.ForeignKey(Neighborhood, null=True)

    #TODO
    #city_id = models.ForeignKey(City)
    #in the meantime:
    city_id = models.IntegerField()

    def __unicode__(self):
        return "Crime # %s" % self.crime_id

    class Meta:
        db_table = 'crime'

class Feature(models.Model):
    feature_id = models.AutoField(primary_key=True, db_column='feature_id')
    name = models.CharField(max_length=100)
    room = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s" % self.name

    class Meta:
        db_table = 'features'
        ordering = ['name']

#TODO: rename ZillowNeighborhood
class Zillow_Neighborhood(models.Model):
    neighborhood_id = models.AutoField(primary_key=True,
                                       db_column='zillow_neighborhood_id')
    name = models.CharField(max_length=256)
    encodedBorder = models.CharField(max_length=1024)
    encodedLevels = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

    #unencoded border property
    def _get_border(self):
        return decode_pairs(self.encodedBorder)

    border = property(_get_border)

    class Meta:
        db_table = 'zillow_neighborhoods'
        ordering = ['name']

class PointsOfInterest(models.Model):
    poi_id = models.AutoField(primary_key=True, db_column='poi_id')
    neighborhood = models.ForeignKey(Neighborhood, null=True)
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    review_points = models.IntegerField()
    num_reviews = models.IntegerField()
    avg_review = models.FloatField()
    popularity = models.IntegerField()
    source_id = models.CharField(max_length=255)
    #no need to retrieve this
    #raw_data = NormalTextField()
    data_type = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'points_of_interest'

class PointsOfInterestTypes(models.Model):
    points_of_interest_types_id = models.AutoField(primary_key=True)
    points_of_interest = models.ForeignKey(PointsOfInterest, related_name='types')
    type = models.CharField(max_length=255)

    def __unicode__(self):  
        return "point_of_interest_type %s" % self.type

    class Meta:
        db_table = 'points_of_interest_types'

class TransitStop(models.Model):
    transit_stop_id = models.AutoField(primary_key=True)
    transit_type = models.CharField(max_length=1024)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=1024)
    route = models.CharField(max_length=1024)
    neighborhood = models.ForeignKey(Neighborhood, null=True)

    def __unicode__(self):
        return "Bus Stop at %s" % self.address

    class Meta:
        db_table = 'transit_stops'

class Park(models.Model):
    park_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1024)
    encodedBorder = models.CharField(max_length=4096)
    encodedLevels = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'parks'

class School(models.Model):
    school_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1024)
    math_score = models.FloatField(null=True)
    reading_score = models.FloatField(null=True)
    city_school_id = models.CharField(max_length=1024)
    school_type = models.CharField(max_length=1024)
    neighborhood = models.ForeignKey(Neighborhood, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "schools"

class Market(models.Model):
    school_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1024)
    address = models.CharField(max_length=4096)
    neighborhood = models.ForeignKey(Neighborhood, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "markets"
