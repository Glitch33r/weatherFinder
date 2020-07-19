from dal import autocomplete
from django import forms

from portal.models import City


class CityFindForm(forms.ModelForm):
    name = forms.ModelChoiceField(
        label='',
        queryset=City.objects.all(),
        widget=autocomplete.ModelSelect2(url='weather-portal:city-autocomplete')
    )

    class Meta:
        model = City
        fields = '__all__'
