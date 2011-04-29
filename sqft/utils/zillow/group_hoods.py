from sqft.search.models import Neighborhood, Zillow_Neighborhood
from utils.crime.crime_locate import is_in

def group_hoods():
    zhoods = Zillow_Neighborhood.objects.all()
    for hood in Neighborhood.objects.all():
        for zhood in zhoods:
            if is_in(hood.center_point, zhood.border):
                hood.zillow_neighborhood = zhood
                hood.save()
                break

def run():
    group_hoods()
