from django.conf.urls import include, url
from django.contrib import admin

from transactions.views import HomeView
from .views import reload_top

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^transactions/', include('transactions.urls', namespace='transactions')),
    url(r'^counterparty/', include('counterparty.urls', namespace='counterparty')),

    url(r'^reload_top/', reload_top, name='reload_top'),

    url(r'^admin/', include(admin.site.urls)),
]
