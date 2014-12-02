from django.conf.urls import url

from counterparty import views

urlpatterns = [
    # url(r'^$', CounterPartyListView.as_view(), name='list'),
    url(r'^(?P<pk>.+)/', views.CounterPartyDetailView.as_view(), name='detail'),
]
