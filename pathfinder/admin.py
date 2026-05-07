# pathfinder/admin.py

from django.contrib import admin
from .models import City, Edge, SearchHistory


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display  = ['name', 'state']
    search_fields = ['name', 'state']
    ordering      = ['name']


@admin.register(Edge)
class EdgeAdmin(admin.ModelAdmin):
    list_display  = ['from_city', 'to_city', 'distance_km']
    search_fields = ['from_city__name', 'to_city__name']


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display  = ['source', 'destination', 'total_distance', 'searched_at']
    ordering      = ['-searched_at']