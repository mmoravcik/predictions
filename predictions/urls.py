from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'predictions.views.home', name='home'),
    # url(r'^predictions/', include('predictions.foo.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'predictions.views.logout_view'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^predict/submit/$', 'predictions.game.views.predict_submit'),
    url(r'^predict/(?P<round_id>\w+)/$', 'predictions.game.views.predict'),
    
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
