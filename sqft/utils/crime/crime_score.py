import MySQLdb


conn = MySQLdb.connect(host="localhost", user="root", db="sqft")
cur = conn.cursor()
cur.execute("""select count(*) crimes, n.neighborhood_id, round(area,2), (count(*) / area) * 100000 rate
from neighborhoods n, crime c
where c.neighborhood_id = n.neighborhood_id
group by name
order by rate desc;""")
all = cur.fetchall()
max_ = max(c[3] for c in all)
for c in all:
    cur = conn.cursor()
    cur.execute("update neighborhoods set crime_rating=%s where neighborhood_id=%s", (c[3]/max_, c[1]))
    cur.close()
conn.commit()
conn.close()
