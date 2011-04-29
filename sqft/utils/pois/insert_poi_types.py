import MySQLdb

conn = MySQLdb.connect(host="localhost", user="root", db="sqft")
#cur = conn.cursor()
#cur.execute("""select poi_id from points_of_interest where
#        categories LIKE '%American%' 
#       OR categories LIKE '%Sushi%' 
#       OR categories LIKE '%Italian%' 
#       OR categories LIKE '%Caribbean%' 
#       OR categories LIKE '%Steakhouses%' 
#       OR categories LIKE '%Chinese%' 
#       OR categories LIKE '%Creperies%' 
#       OR categories LIKE '%Restaurants%' 
#       OR categories LIKE '%Spanish%' 
#       OR categories LIKE '%Burgers%' 
#       OR categories LIKE '%Seafood%' 
#       OR categories LIKE '%Diners%' 
#       OR categories LIKE '%Tapas%' 
#       OR categories LIKE '%Mediterranian%' 
#       OR categories LIKE '%Breakfast%' 
#       OR categories LIKE '%Thai%' 
#       OR categories LIKE '%Afghani%' 
#       OR categories LIKE '%Indian%' 
#       OR categories LIKE '%Nepalese%' 
#       OR categories LIKE '%Greek%' 
#       OR categories LIKE '%Bagels%' 
#       OR categories LIKE '%Southern%' 
#       OR categories LIKE '%Mexican%'""")
#dining_poi = cur.fetchall()
#
#cur = conn.cursor()
#for d in dining_poi:
#    cur.execute("""insert into points_of_interest_types
#                    (points_of_interest_id, type)
#                    values (%s, 'dining')""", (d[0]))
#    cur.close()
#    cur = conn.cursor()

cur = conn.cursor()
cur.execute("""select poi_id from points_of_interest where
categories LIKE '%Adult%' 
OR categories LIKE '%Wine%' 
OR categories LIKE '%Bars%' 
OR categories LIKE '%Music%' 
OR categories LIKE '%Clubs%' 
OR categories LIKE '%Pubs%' 
OR categories LIKE '%Karaoke%' 
OR categories LIKE '%Lounges%' 
OR categories LIKE '%Jazz%' 
OR categories LIKE '%Pool Halls%'""")
nightlife_poi = cur.fetchall()

cur = conn.cursor()
for d in nightlife_poi:
    cur.execute("""insert into points_of_interest_types
                    (points_of_interest_id, type)
                    values (%s, 'nightlife')""", (d[0]))
    cur.close()
    cur = conn.cursor()
cur.close()

conn.commit()
conn.close()
