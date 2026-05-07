# pathfinder/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('',             views.index,     name='index'),
    path('find-path/',   views.find_path, name='find_path'),
    path('add-city/',    views.add_city,  name='add_city'),
    path('add-edge/',    views.add_edge,  name='add_edge'),
    path('history/',     views.history,   name='history'),
]