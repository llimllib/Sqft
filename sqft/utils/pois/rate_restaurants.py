#create the restaurant ratings
#run with ./manage.py runscript --traceback utils.rate_restaurants
#assuming you've installed django-extensions
#
#this is intended to be readable, not efficient. Improve if it ever matters.
#
from sqft.search.models import PointsOfInterest, Neighborhood

def rate_restaurants():
    # pull all pois with a hood
    pois = PointsOfInterest.objects.filter(neighborhood__isnull=False,
                                           types__type__exact='dining')
    max_pop = max(p.popularity for p in pois)

    #and all hoods
    hoods = Neighborhood.objects.all()
    poi_dict = dict((h.name, []) for h in hoods)

    # transform it into a dictionary {'hood': [pois in that hood]}
    for p in pois:
        poi_dict[p.neighborhood.name].append(p)

    #now calculate a raw score for each neighborhood
    #scores we have: popularity 0-80
    #                avg_review 0-5
    raw_scores = {}
    for hood, poi_list in poi_dict.iteritems():
        if not len(poi_list):
            raw_scores[hood] = 0
            continue 

        popular = [p.popularity for p in poi_list if p.popularity > 0]
        reviewed = [p.avg_review for p in poi_list if p.avg_review > 0]

        #assume that a neighborhood sucks if it has 0 restaurants reviewed or popular
        if not popular or not reviewed:
            raw_scores[hood] = 0
            print "hood %s sucks and gets a zero" % hood
            continue

        pop_pct = float(sum(popular)) / (max_pop * len(popular))
        rev_pct = float(sum(reviewed)) / (5 * len(reviewed))
        raw_scores[hood] = pop_pct + rev_pct

    #then normalize it and save it
    max_raw = max(raw_scores[hood] for hood in raw_scores)
    for hood in raw_scores:
        normalized_score = raw_scores[hood] / max_raw
        h = Neighborhood.objects.get(name=hood)
        h.restaurant_rating = normalized_score
        h.save()

def run():
    #make sure you run find_poi_hoods in score_nightlife.py before running this
    rate_restaurants()
