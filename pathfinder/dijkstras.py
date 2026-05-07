# pathfinder/dijkstra.py

import heapq
from .models import Edge, City


def build_graph():
    """
    Reads all Edge rows from DB and builds an adjacency dict.

    Returns:
        { city_id: [(neighbour_id, distance_km), ...] }
    """
    graph = {}

    # Pre-populate all cities so isolated cities don't break Dijkstra
    for city in City.objects.all():
        graph[city.id] = []

    # Build adjacency list from edges
    edges = Edge.objects.select_related('from_city', 'to_city').all()

    for edge in edges:
        f = edge.from_city.id
        t = edge.to_city.id
        d = edge.distance_km

        graph[f].append((t, d))
        graph[t].append((f, d))   # undirected — both directions

    return graph


def build_path(previous, start, end):
    """
    Reconstructs ordered list of city IDs from start → end
    using the 'previous' dict built during Dijkstra.

    Returns list of city IDs on success, None if no valid path.
    """
    path    = []
    current = end

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    if path[0] != start:
        return None

    return path


def resolve_path_names(path_ids):
    """
    Converts a list of city IDs into city names.
    Used before saving to SearchHistory.path_json.

    Returns:
        ["Mumbai", "Pune", "Hyderabad", ...]
    """
    cities = City.objects.filter(id__in=path_ids).in_bulk()
    return [cities[city_id].name for city_id in path_ids]


def dijkstra(graph, start, end):
    """
    Finds the shortest path between start and end.

    Parameters:
        graph : { city_id: [(neighbour_id, distance_km), ...] }
        start : int  (City.id)
        end   : int  (City.id)

    Returns:
        (path_ids, total_distance)   on success  →  ([1, 4, 7], 520)
        (None, None)                 if no path exists
    """
    if start not in graph or end not in graph:
        return None, None

    distances = {city: float('inf') for city in graph}
    previous  = {city: None        for city in graph}
    distances[start] = 0

    heap = []
    heapq.heappush(heap, (0, start))

    while heap:
        current_dist, current_node = heapq.heappop(heap)

        # Stale entry — shorter path already found
        if current_dist > distances[current_node]:
            continue

        # Reached destination — stop early
        if current_node == end:
            break

        for neighbour, weight in graph[current_node]:
            new_dist = current_dist + weight

            if new_dist < distances[neighbour]:
                distances[neighbour] = new_dist
                previous[neighbour]  = current_node
                heapq.heappush(heap, (new_dist, neighbour))

    # Destination never reached
    if distances[end] == float('inf'):
        return None, None

    path_ids = build_path(previous, start, end)
    return path_ids, distances[end]