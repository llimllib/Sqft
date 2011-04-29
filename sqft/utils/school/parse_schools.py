from os.path import dirname, join
from urllib import urlopen
from time import sleep
import cPickle
import re

from sqft.search.models import School, Neighborhood
from sqft.utils.geopy.geocoders import Google, Yahoo
from sqft.utils.crime.crime_locate import is_in

def get_schoollist():
    f = open(join(dirname(__file__), "school_list.html"))
    schools = {}

    for line in f:
        school_types = [('Elementary/Middle Schools', 'elem_middle'),
                        ('Middle/High Schools', 'middle_high'),
                        ('Special/Alternative Schools', 'special'),
                        ('Elementary Schools', 'elementary'),
                        ('Middle Schools', 'middle'),
                        ('High Schools', 'high'),
                        ('K through 12" Schools', 'k12')]
        for type, code in school_types:
            if type in line:
                school_type = code
                schools[school_type] = []
                break
        
        r = re.search('schoolBox">(.*?) \((\d*)\)<', line)
        if r:
            school, number = r.groups()
            schools[school_type].append((school, number))
    return schools

def get_scores(schools):
    url = "http://www.mdreportcard.org/Assessments.aspx?K=30%s&WDATA=School"
    scores = {}
    for school, number in schools['elem_middle']:
        scores[school] = []

        print "fetching %s" % school
        dat = urlopen(url % number)
        #dat = file("elementary.html")

        col = -1
        grade = None

        for line in dat:
            # we only want to gather data when we're in a <div MSAgrade4all></div>
            r = re.search('<div id="MSAgrade(\d+)all', line)
            if r: grade = r.groups()[0]
            r = re.search('</div>', line)
            if r: grade = None

            cols = ["title", "math", "reading", "science"]
            if grade and "<td" in line: col += 1

            r = re.search("<img.*?<img.*?<img.*?\>.*?([\d.]+)<img", line)
            if r and grade:
                scores[school].append((cols[col % 4], float(r.groups()[0])))

    #for school, number in schools['high']:
    #    scores[school] = []

    #    print "fetching %s" % school
    #    dat = urlopen(url % number)
    #    #dat = file("utils/school/high.html")

    #    col = -1
    #    grade = None

    #    for line in dat:
    #        # we only want to gather data when we're in a <div MSAgrade4all></div>
    #        r = re.search('<div id="(?:ENGLISH2|ALGEBRA)grade(\d+)all', line)
    #        if r: grade = r.groups()[0]
    #        r = re.search('</div>', line)
    #        if r: grade = None

    #        cols = ["title", "math", "reading", "science"]
    #        if grade and "<td" in line: col += 1

    #        r = re.search("<img.*?<img.*?<img.*?\>.*?([\d.]+)<img", line)
    #        if r and grade:
    #            scores[school].append((cols[col % 4], float(r.groups()[0])))

    return scores

def create_schools(schools_dict):
    all_scores = {}
    for score_pickle in ["elementary", "middle", "high", "elem_middle"]:
        all_scores[score_pickle] = cPickle.load(file("utils/school/" + score_pickle + ".pkl"))

    for school_type, school_list in schools_dict.iteritems():
        if school_type in all_scores:
            for school, school_number in school_list:
                #a list of tuples [('math', x.xx), ('reading', x.xx)...]
                scores = all_scores[school_type][school]
                if not len(scores):
                    s = School(name=school,
                               city_school_id=school_number,
                               school_type=school_type)
                else:
                    #I stored the grades for middle schools. Throw them away
                    if len(scores[0]) == 3: i,j = 2,1
                    else:                   i,j = 1,0
                    math_score = sum(x[i] for x in scores if x[j]=='math')
                    math_len = float(len([x for x in scores if x[j]=='math']))
                    reading_score = sum(x[i] for x in scores if x[j]=='reading')
                    reading_len = float(len([x for x in scores if x[j]=='reading']))
                    s = School(name=school,
                               city_school_id=school_number,
                               math_score=math_score/math_len,
                               reading_score=reading_score/reading_len,
                               school_type=school_type)
                s.save()
        else:
            for school, school_number in school_list:
                s = School(name=school,
                           city_school_id=school_number,
                           school_type=school_type)
                s.save()

#g = Google('ABQIAAAAi38qWc-9V8q5b6bgPClsfxTfKEWMeMOdp19wa3uONsY3R1LXvRTgTR8o6snPUFoi7M-AG31rpq6VWQ')
g = Yahoo('bKVpVX_V34Ec62VfSmdXD1Sow.dHyfSQfxCp5qeug95VuX1.mxPFUZvqYDR1HUb8WOyE.d.q')
def geocode(addr):
    gc = list(g.geocode(addr, False))
    if not len(gc):
        sleep(2)
        gc = list(g.geocode(addr, False))
        if not len(gc):
            print "couldn't find: %s" % addr
            return None
    #we only want the best result
    gc = gc[0]
    if type(gc[0]) != type(u''):
        print gc, " is not what I was expecting"
        raise Exception("wtf duder %s" % addr)
    return (gc[0], gc[1])

def geolocate_schools():
    for school in School.objects.all():
        if not school.latitude:
            print school
            gc = geocode(school.name + ", baltimore, md")
            if not gc: continue
            addr, (lat, lon) = gc
            school.latitude = lat
            school.longitude = lon
            school.save()

def find_school_hoods():
    hoods = Neighborhood.objects.all()
    for school in School.objects.all():
        for hood in hoods:
            if is_in((school.latitude, school.longitude), hood.border):
                school.neighborhood = hood
                school.save()
                break

def rate_hood_schools():
    hoods = []
    for hood in Neighborhood.objects.all():
        schools = hood.school_set.all()

        if not schools:
            hoods.append((0, hood))
            continue

        scores = []
        for school in schools:
            if school.math_score: scores.append(school.math_score)
            if school.reading_score: scores.append(school.reading_score)
        hoods.append((sum(scores)/float(len(scores)), hood))

    maxscore, _ = max(hoods)
    for score, hood in hoods:
        hood.school_rating = score/maxscore
        hood.save()

def run():
    #schools = get_schoollist()
    #I ran this procedures manually and pickled the results
    #get_scores(schools)
    #create_schools(schools)
    #geolocate_schools()
    find_school_hoods()
    rate_hood_schools()
