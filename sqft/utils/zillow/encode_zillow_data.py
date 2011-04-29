import md_hoods
import MySQLdb
from decodegmap import encode_points, decode_points
from glineenc import encode_pairs

def flatten(pts):
    x = []
    for lat, long in pts:
        x.append(lat)
        x.append(long)
    return x

for name, pts in md_hoods.hoods.iteritems():
    b, l = encode_pairs(pts)
    conn = MySQLdb.connect(host="localhost", user="root", db="sqft")
    cur = conn.cursor()
    cur.execute("""insert into zillow_neighborhoods(name, encodedBorder, encodedLevels)
                   values (%s, %s, %s)""",
                   (name, b, l))
    cur.close()
conn.commit()
