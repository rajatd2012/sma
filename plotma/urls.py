from django.conf.urls import patterns, url
from plotma import views
from django.conf import settings

urlpatterns = patterns('',

      url(r'^$', 
			views.index, 
			name='index'),

)
