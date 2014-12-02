from django.conf.urls import url

from counterparty import views

urlpatterns = [
    url(r'^$', views.CounterPartyListView.as_view(), name='list'),
    url(r'^(?P<pk>.+)/', views.CounterPartyDetailView.as_view(), name='detail'),
    url(r'create/', views.CreatePatternedCounterPartyView.as_view(), name='create'),
    url(r'pattern_matches/', views.AliasPatternMatchesView.as_view(), name='pattern_matches')
]
