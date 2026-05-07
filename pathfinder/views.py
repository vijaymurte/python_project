# pathfinder/views.py

import json
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import City, Edge, SearchHistory
from .forms import RouteForm, CityForm, EdgeForm
from .dijkstras import build_graph, dijkstra, resolve_path_names


# ── Helper: builds context for index.html (map needs all_cities_json) ──
def _index_context(form):
    all_cities = City.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    )
    all_cities_json = json.dumps([
        {
            'name'  : city.name,
            'state' : city.state,
            'lat'   : float(city.latitude),
            'lng'   : float(city.longitude),
        }
        for city in all_cities
    ])
    return {'form': form, 'all_cities_json': all_cities_json}


def index(request):
    form = RouteForm()
    return render(request, 'pathfinder/index.html', _index_context(form))


def find_path(request):
    if request.method != 'POST':
        return redirect('index')

    form = RouteForm(request.POST)

    if not form.is_valid():
        return render(request, 'pathfinder/index.html', _index_context(form))

    source      = form.cleaned_data['source']
    destination = form.cleaned_data['destination']

    if source == destination:
        messages.error(request, "Source and destination cannot be the same city.")
        return render(request, 'pathfinder/index.html', _index_context(form))

    graph          = build_graph()
    path_ids, dist = dijkstra(graph, source.id, destination.id)

    if path_ids is None:
        messages.error(request, f"No route found between {source.name} and {destination.name}.")
        return render(request, 'pathfinder/index.html', _index_context(form))

    path_names = resolve_path_names(path_ids)

    # Build ordered coordinates for Leaflet
    city_map    = City.objects.filter(id__in=path_ids).in_bulk()
    path_coords = json.dumps([
        {
            'name' : city_map[city_id].name,
            'lat'  : float(city_map[city_id].latitude),
            'lng'  : float(city_map[city_id].longitude),
        }
        for city_id in path_ids
        if city_map[city_id].latitude and city_map[city_id].longitude
    ])

    SearchHistory.objects.create(
        source         = source,
        destination    = destination,
        path_json      = path_names,
        total_distance = dist,
    )

    context = {
        'source'      : source.name,
        'destination' : destination.name,
        'path'        : path_names,
        'distance'    : dist,
        'path_coords' : path_coords,
    }
    return render(request, 'pathfinder/result.html', context)


def add_city(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.save()
            messages.success(request, f"{city.name} added successfully.")
            return redirect('add_city')
    else:
        form = CityForm()

    return render(request, 'pathfinder/add_city.html', {'form': form})


def add_edge(request):
    if request.method == 'POST':
        form = EdgeForm(request.POST)
        if form.is_valid():
            from_city = form.cleaned_data['from_city']
            to_city   = form.cleaned_data['to_city']

            if from_city == to_city:
                messages.error(request, "A city cannot connect to itself.")
                return render(request, 'pathfinder/add_edge.html', {'form': form})

            already_exists = Edge.objects.filter(
                from_city=from_city, to_city=to_city
            ).exists() or Edge.objects.filter(
                from_city=to_city, to_city=from_city
            ).exists()

            if already_exists:
                messages.error(request, f"A road between {from_city.name} and {to_city.name} already exists.")
                return render(request, 'pathfinder/add_edge.html', {'form': form})

            edge = form.save()
            messages.success(request, f"Road from {edge.from_city.name} to {edge.to_city.name} ({edge.distance_km} km) added.")
            return redirect('add_edge')
    else:
        form = EdgeForm()

    return render(request, 'pathfinder/add_edge.html', {'form': form})


def history(request):
    searches = SearchHistory.objects.select_related('source', 'destination').all()
    return render(request, 'pathfinder/history.html', {'searches': searches})