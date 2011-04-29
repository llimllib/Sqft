import urllib, re
from pprint import pprint as pp
from datetime import datetime, timedelta
from sqft.utils.geopy.geocoders import Google
import MySQLdb
from time import sleep

bcpd_arc_url = "http://maps.baltimorepolice.org/servlet/com.esri.esrimap.Esrimap?ServiceName=BaltimorePolice&CustomService=Query&ClientVersion=3.1&Form=True&Encode=False"

districts={"Northwest":
"""<POINT x="1393926.78398081" y="621171.476883567" />
<POINT x="1397217.83" y="621171.476883567" />
<POINT x="1397217.83" y="616180.92" />
<POINT x="1393926.78398081" y="616180.92" />""",

"Northeast":
"""<POINT x="1442316.71979371" y="621406.8125" />
<POINT x="1445310.91155006" y="621406.8125" />
<POINT x="1445310.91155006" y="618412.039570119" />
<POINT x="1442316.71979371" y="618412.039570119" />""",

"West":
"""<POINT x="1394077.54114138" y="592162.660878078" />
<POINT x="1397806.49013248" y="592162.660878078" />
<POINT x="1397806.49013248" y="586906.339042239" />
<POINT x="1394077.54114138" y="586906.339042239" />""",

"East":
"""<POINT x="1442360.22501292" y="590833.205731698" />
<POINT x="1445457.16335056" y="590833.205731698" />
<POINT x="1445457.16335056" y="584158.004589979" />
<POINT x="1442360.22501292" y="584158.004589979" />""",

"South":
"""<POINT x="1428897.34236402" y="565462.027408424" />
<POINT x="1444872.773" y="565462.027408424" />
<POINT x="1444872.773" y="557733.625" />
<POINT x="1428897.34236402" y="557733.625" />""",

"Whole City":
"""<POINT x="1393926.78398081" y="621406.8125" />
<POINT x="1442360.22501292" y="621406.8125" />
<POINT x="1442360.22501292" y="557733.625" />
<POINT x="1393926.78398081" y="557733.625" />""",
}

#XXX: note the extra "> right before SPATIALFILTER... sigh.
def requestXML(dt):
    return """<?xml version="1.0" encoding="UTF-8" ?><ARCXML version="1.1">
    <REQUEST>
    <GET_FEATURES outputmode="xml" envelope="true" geometry="false" featurelimit="1000" beginrecord="1">
    <LAYER id="6" /><SPATIALQUERY subfields="CCNO CRIME_DESC FROM_DATE PREM_DESC LOCATION POST DISTRICT" where="(FROM_DATE &gt;&#061; {ts '%s'}) AND (FROM_DATE &lt;&#061; {ts '%s'})"> "><SPATIALFILTER relation="area_intersection" ><POLYGON>
    <RING>
    %s
    </RING>
    </POLYGON>
    </SPATIALFILTER></SPATIALQUERY></GET_FEATURES></REQUEST></ARCXML>""" % \
    (dt.isoformat(' '), (dt + timedelta(1)).isoformat(' '), districts["Whole City"])

#return a list of tuples of (ccno, crime type, premises, time, address, post (?), district)
def scrape(dt):
    postdata = urllib.urlencode({'ArcXMLRequest': requestXML(dt)})
    d = urllib.urlopen(bcpd_arc_url, postdata).read()
    xml = re.search("(<?xml.*)';", d).groups()[0]
    #skip actual parsing of the xml, for now. KISS
    fs = re.findall("(FIELDS.*?)>", xml)
    ts = [list(re.search('FIELDS CCNO="(.*?)" CRIME_DESC="(.*?)" PREM_DESC="(.*?)" FROM_DATE="(.*?)" LOCATION="(.*?)" POST="(.*?)" DISTRICT="(.*?)"', f).groups()) for f in fs]
    for t in ts:
        #time is given in milliseconds since unix time start; we want seconds
        t[3] = datetime.fromtimestamp(float(t[3])/1000)
    return [tuple(t) for t in ts]

#s = scrape(datetime(2009,2,10))
#pp((s, len(s)))

#geocode the addys
def date_range(dt1, dt2):
    if dt1 > dt2:
        raise Exception("invalid date range")
    while dt1 <= dt2:
        yield dt1
        dt1 += timedelta(days=1)

g = Google('ABQIAAAAi38qWc-9V8q5b6bgPClsfxTfKEWMeMOdp19wa3uONsY3R1LXvRTgTR8o6snPUFoi7M-AG31rpq6VWQ')
def geocode(addr):
    for _, coords in g.geocode(addr + " baltimore, md", False):
        return coords

conn = MySQLdb.connect(host="localhost", user="root", db="sqft")
notfound = []
#first round: 2009,1,1 to 2009,3,9
#round 2: 2009,3,10 to 2009,5,12
for d in date_range(datetime(2009,3,10), datetime(2009,5,12)):
    print d
    for s in scrape(d):
        case_number, crime, premises, dt, addr, post, district = s
        latlong = geocode(addr)
        if not latlong:
            sleep(2)
            latlong = geocode(addr)
            if not latlong:
                notfound.append(addr)
                continue
        lat, long = latlong
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO crime (city_id, case_number, crime, location, address,
                               reported_on, latitude, longitude)
            VALUES (1,%s,%s,%s,%s,%s,%s,%s)""" , (
                case_number, crime, premises, addr, dt, lat, long)
        )
        cur.close()
        conn.commit()
print "not found addresses:"
pp(notfound)
