from django.conf.urls import patterns, include, url
from django.contrib import admin

from transactions.views import HomeView

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='home'),
    # url(r'^transactions/', include('transactions.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
