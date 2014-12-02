from django.conf.urls import include, url
from django.contrib import admin

from transactions.views import HomeView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^counterparty/', include('counterparty.urls', namespace='counterparty')),

    url(r'^admin/', include(admin.site.urls)),
]
