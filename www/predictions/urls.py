from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'predictions.views.home', name='home'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'predictions.views.logout_view'),
    url(r'^round/predict/submit/$', 'predictions.game.views.predict_submit'),
    url(r'^round/results/(?P<round_id>\w+)$', 'predictions.game.views.round_results'),
    url(r'^round/predict/(?P<round_id>\w+)/$', 'predictions.game.views.predict'),
    url(r'^registration/$', 'predictions.views.register'),
    url(r'^rules/$', 'predictions.views.rules'),
    url(r'^admin/', include(admin.site.urls)),
)