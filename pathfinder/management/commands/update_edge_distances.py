# pathfinder/management/commands/update_edge_distances.py

import time
import requests
from django.core.management.base import BaseCommand
from pathfinder.models import Edge


OSRM_URL = "http://router.project-osrm.org/route/v1/driving/{lng1},{lat1};{lng2},{lat2}?overview=false"


def get_real_distance(from_city, to_city):
    """
    Calls OSRM API with coordinates of two cities.
    Returns real road distance in km, or None if request fails.
    """
    try:
        url = OSRM_URL.format(
            lng1 = float(from_city.longitude),
            lat1 = float(from_city.latitude),
            lng2 = float(to_city.longitude),
            lat2 = float(to_city.latitude),
        )
        response = requests.get(url, timeout=10)
        data     = response.json()

        if data.get('code') == 'Ok':
            # OSRM returns distance in meters — convert to km
            distance_km = data['routes'][0]['distance'] / 1000
            return round(distance_km)
        else:
            return None

    except Exception as e:
        return None


class Command(BaseCommand):
    help = 'Updates all edge distances with real road distances from OSRM'

    def handle(self, *args, **kwargs):
        edges = Edge.objects.select_related('from_city', 'to_city').all()

        self.stdout.write(f"Found {edges.count()} edges to update.\n")

        updated = 0
        failed  = 0

        for edge in edges:
            from_city = edge.from_city
            to_city   = edge.to_city

            # Skip if coordinates are missing
            if not all([
                from_city.latitude, from_city.longitude,
                to_city.latitude,   to_city.longitude
            ]):
                self.stdout.write(
                    f"  SKIP — missing coordinates: {from_city.name} ↔ {to_city.name}"
                )
                failed += 1
                continue

            old_distance = edge.distance_km
            new_distance = get_real_distance(from_city, to_city)

            if new_distance is None:
                self.stdout.write(
                    f"  FAIL — OSRM error: {from_city.name} ↔ {to_city.name}"
                )
                failed += 1
                continue

            edge.distance_km = new_distance
            edge.save()
            updated += 1

            self.stdout.write(
                f"  OK — {from_city.name} ↔ {to_city.name}: "
                f"{old_distance} km → {new_distance} km"
            )

            # Be polite to OSRM public server — 1 request per second
            time.sleep(1)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {updated} edges updated, {failed} failed."
        ))