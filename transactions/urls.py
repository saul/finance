from django.conf.urls import url

from transactions import views

urlpatterns = [
    url(r'in_out_data/(?P<year>\d+)/(?P<month>\d+)/$', views.IncomingOutgoingDataView.as_view(), name='in_out_data'),
    url(r'categorise/$', views.CategoriseView.as_view(), name='categorise')
]
