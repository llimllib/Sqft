from sqft.search.models import Neighborhood

def run():
    hoods = Neighborhood.objects.all()
    for rating in ["crime_rating", "restaurant_rating", "nightlife_rating", "transit_rating",
                   "park_rating", "market_rating"]:
        ratings = [(getattr(h, rating), h) for h in hoods]
        ratings.sort()
        grade_name = rating.split("_")[0] + "_grade"
        for rating, hood in ratings:
            if rating >= .8: setattr(hood, grade_name, 'A')
            elif rating >= .6: setattr(hood, grade_name, 'B')
            elif rating >= .4: setattr(hood, grade_name, 'B')
            elif rating >= .2: setattr(hood, grade_name, 'C')
            else:              setattr(hood, grade_name, 'C')
            hood.save()

if __name__=="__main__":
    run()
