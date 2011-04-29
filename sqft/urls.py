from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^/?$', 'sqft.search.views.search'),

    (r'^search/?$', 'sqft.search.views.search'),
    (r'^search/results$', 'sqft.search.views.results'),
	(r'^rental$', 'sqft.search.views.rental'),
    (r'^search/page_hoods$', 'sqft.search.views.page_hoods'),
    (r'^search/distance$', 'sqft.search.views.distance_from_address'),
    (r'^search/hood_pics$', 'sqft.search.views.get_flickr_pics'),
    (r'^search/points_of_interest$', 'sqft.search.views.points_of_interest'),

    #debug views
    (r'^debug/hoods$', 'sqft.debug.views.hoods'),
    (r'^debug/crimes$', 'sqft.debug.views.crimes'),
    (r'^debug/zhoods$', 'sqft.debug.views.zillow_hoods'),
    (r'^debug/pois$', 'sqft.search.views.points_of_interest'),
    (r'^debug/transit_stops$', 'sqft.debug.views.transit_stops'),
    (r'^debug/parks$', 'sqft.debug.views.parks'),
    (r'^debug/centers$', 'sqft.debug.views.centers'),
    (r'^debug/schools$', 'sqft.debug.views.schools'),
    (r'^debug/markets$', 'sqft.debug.views.markets'),

    (r'^debug$', 'sqft.debug.views.debug_map'),
    (r'^debug/grades$', 'sqft.debug.views.grades'),

    (r'^admin/(.*)', admin.site.root),

    (r'^public/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/Users/llimllib/code/sqft/static/'}),
)
