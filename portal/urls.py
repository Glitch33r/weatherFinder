
from django.urls import path

from portal.views import *

app_name = 'weather-portal'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('result', result_view, name='results'),
    path('start-finding', submit_find_weather, name='start-find'),
    path('city-autocomplete/', CityAutocomplete.as_view(), name='city-autocomplete'),
]
