# pathfinder/forms.py

from django import forms
from .models import City, Edge


class RouteForm(forms.Form):
    source = forms.ModelChoiceField(
        queryset=City.objects.all().order_by('name'),
        label='Source City',
        empty_label='-- Select Source --'
    )
    destination = forms.ModelChoiceField(
        queryset=City.objects.all().order_by('name'),
        label='Destination City',
        empty_label='-- Select Destination --'
    )


class CityForm(forms.ModelForm):
    class Meta:
        model  = City
        fields = ['name', 'state', 'latitude', 'longitude']

    def clean_name(self):
        name = self.cleaned_data['name'].strip().title()
        if City.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError(f"{name} already exists.")
        return name

    def clean_state(self):
        return self.cleaned_data['state'].strip().title()

    def clean_latitude(self):
        lat = self.cleaned_data.get('latitude')
        if lat is None:
            raise forms.ValidationError("Latitude is required.")
        if not (-90 <= float(lat) <= 90):
            raise forms.ValidationError("Latitude must be between -90 and 90.")
        return lat

    def clean_longitude(self):
        lng = self.cleaned_data.get('longitude')
        if lng is None:
            raise forms.ValidationError("Longitude is required.")
        if not (-180 <= float(lng) <= 180):
            raise forms.ValidationError("Longitude must be between -180 and 180.")
        return lng


class EdgeForm(forms.ModelForm):
    class Meta:
        model  = Edge
        fields = ['from_city', 'to_city', 'distance_km']

    def clean_distance_km(self):
        distance = self.cleaned_data['distance_km']
        if distance <= 0:
            raise forms.ValidationError("Distance must be greater than 0.")
        if distance > 5000:
            raise forms.ValidationError("Distance cannot exceed 5000 km.")
        return distance