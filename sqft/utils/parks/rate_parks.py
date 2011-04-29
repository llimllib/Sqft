from sqft.search.models import Park, Neighborhood
from sqft.utils.geopy.distance import distance
from sqft.utils.decodegmap import decode_pairs

def rate_parks():
    pts = []
    for p in Park.objects.all():
        pts.extend(decode_pairs(p.encodedBorder))
    distances = []
    #I suspect that the Hausdorff distance will be better for this:
    #http://cgm.cs.mcgill.ca/~godfried/teaching/cg-projects/98/normand/main.html
    #http://en.wikipedia.org/wiki/Hausdorff_distance
    for n in Neighborhood.objects.all():
        m = min(distance(pt, npt).meters for pt in pts for npt in n.border)
        distances.append((m, n))
    maxm = float(max(distances)[0])
    for m, hood in distances:
        hood.park_rating = m/maxm
        hood.save()

def run():
    rate_parks()

if __name__ == "__main__": run()
