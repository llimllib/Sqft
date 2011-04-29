import random

def _make_pairs(pts):
    pairs = []
    it = iter(pts)
    for i in it:
        pairs.append((i, it.next()))
    return pairs

def decode_pairs(encodedBorder):
    return _make_pairs(decode_points(encodedBorder))

def decode_points(points):
    """Decodes a string of locations encoded using the GMap encoding
    Accepts the encoded string and
    returns an array of lat/lon pairs [lat1,lon1,lat2,lon2,...]"""
    if not points:
        return []
    Ch = len(points)
    pb = 0
    locations = []
    Ka = 0
    Pa = 0
    while pb < Ch:
        oc = 0
        Fa = 0
        while 1:
            ub = ord(points[pb])-63
            pb += 1
            Fa |= (ub&31)<<oc
            oc += 5
            if ub < 32: break
        if Fa & 1: i = ~(Fa>>1)
        else: i = Fa>>1
        Ka = Ka+i
        locations.append(Ka*1.0E-5)

        oc = 0
        Fa = 0
        while 1:
            ub = ord(points[pb])-63
            pb += 1
            Fa |= (ub&31)<<oc
            oc += 5
            if ub < 32: break
        if Fa & 1: i = ~(Fa>>1)
        else: i = Fa>>1
        Pa = Pa+i

        locations.append(Pa*1.0E-5)

    return locations



def encode_points(locations):
    """Encodes lat/lon locations into a Gmap polyline encoding.
    Accepts an array of lat/lon pairs [lat1,lon1,lat2,lon2,...] and
    returns 2 strings, the encoded points and the corresponding levels"""

    if not locations or len(locations) < 2:
        return "", ""
   
    numLocations = len(locations)/2
    locations = map( lambda x: int(x/1.0E-5), locations )
    points = []
    levels = []
    xo = yo = 0
    for i in range(numLocations):
        y = locations[i<<1]
        yd = y - yo
        yo = y
        f = (abs(yd) << 1) - (yd<0)
        while 1:
            e = f & 31
            f >>= 5
            if f:
                e |= 32
            points.append(chr(e+63))
            if f == 0: break

        x = locations[(i<<1)+1]
        xd = x - xo
        xo = x
        f = (abs(xd) << 1) - (xd<0)
        while 1:
            e = f & 31
            f >>= 5
            if f:
                e |= 32
            points.append(chr(e+63))
            if f == 0: break

        levels.append(nextLevel())
    levels[0] = 'B'
    levels[-1] = 'B'
    return "".join(points), "".join(levels)

def nextLevel():
    r = random.random()
    if r < 0.65: return '?'
    if r < 0.92: return '@'
    if r < 0.97: return 'A'
    return 'B'
