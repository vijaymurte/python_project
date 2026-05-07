import time
import requests
from django.core.management.base import BaseCommand
from pathfinder.models import City, Edge


def get_osrm_distance(from_city, to_city):
    try:
        url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{float(from_city.longitude)},{float(from_city.latitude)};"
            f"{float(to_city.longitude)},{float(to_city.latitude)}"
            f"?overview=false"
        )
        response = requests.get(url, timeout=10)
        data     = response.json()
        if data.get('code') == 'Ok':
            return round(data['routes'][0]['distance'] / 1000)
        return None
    except Exception:
        return None


CITIES = [
    # Tier 1
    ("Mumbai",              "Maharashtra",          19.0760,    72.8777),
    ("Delhi",               "Delhi",                28.6139,    77.2090),
    ("Bangalore",           "Karnataka",            12.9716,    77.5946),
    ("Hyderabad",           "Telangana",            17.3850,    78.4867),
    ("Chennai",             "Tamil Nadu",           13.0827,    80.2707),
    ("Kolkata",             "West Bengal",          22.5726,    88.3639),
    ("Pune",                "Maharashtra",          18.5204,    73.8567),
    ("Ahmedabad",           "Gujarat",              23.0225,    72.5714),

    # Tier 2
    ("Jaipur",              "Rajasthan",            26.9124,    75.7873),
    ("Lucknow",             "Uttar Pradesh",        26.8467,    80.9462),
    ("Kanpur",              "Uttar Pradesh",        26.4499,    80.3319),
    ("Nagpur",              "Maharashtra",          21.1458,    79.0882),
    ("Indore",              "Madhya Pradesh",       22.7196,    75.8577),
    ("Bhopal",              "Madhya Pradesh",       23.2599,    77.4126),
    ("Visakhapatnam",       "Andhra Pradesh",       17.6868,    83.2185),
    ("Patna",               "Bihar",                25.5941,    85.1376),
    ("Vadodara",            "Gujarat",              22.3072,    73.1812),
    ("Surat",               "Gujarat",              21.1702,    72.8311),
    ("Coimbatore",          "Tamil Nadu",           11.0168,    76.9558),
    ("Madurai",             "Tamil Nadu",            9.9252,    78.1198),
    ("Kochi",               "Kerala",                9.9312,    76.2673),
    ("Thiruvananthapuram",  "Kerala",                8.5241,    76.9366),
    ("Guwahati",            "Assam",                26.1445,    91.7362),
    ("Bhubaneswar",         "Odisha",               20.2961,    85.8245),
    ("Raipur",              "Chhattisgarh",         21.2514,    81.6296),
    ("Ranchi",              "Jharkhand",            23.3441,    85.3096),
    ("Amritsar",            "Punjab",               31.6340,    74.8723),
    ("Ludhiana",            "Punjab",               30.9010,    75.8573),
    ("Chandigarh",          "Punjab",               30.7333,    76.7794),
    ("Dehradun",            "Uttarakhand",          30.3165,    78.0322),
    ("Agra",                "Uttar Pradesh",        27.1767,    78.0081),
    ("Varanasi",            "Uttar Pradesh",        25.3176,    82.9739),
    ("Meerut",              "Uttar Pradesh",        28.9845,    77.7064),
    ("Nashik",              "Maharashtra",          19.9975,    73.7898),
    ("Aurangabad",          "Maharashtra",          19.8762,    75.3433),
    ("Rajkot",              "Gujarat",              22.3039,    70.8022),
    ("Jodhpur",             "Rajasthan",            26.2389,    73.0243),
    ("Udaipur",             "Rajasthan",            24.5854,    73.7125),
    ("Kota",                "Rajasthan",            25.2138,    75.8648),
    ("Jabalpur",            "Madhya Pradesh",       23.1815,    79.9864),
    ("Gwalior",             "Madhya Pradesh",       26.2183,    78.1828),
    ("Vijayawada",          "Andhra Pradesh",       16.5062,    80.6480),
    ("Tiruchirappalli",     "Tamil Nadu",           10.7905,    78.7047),
    ("Salem",               "Tamil Nadu",           11.6643,    78.1460),
    ("Mysuru",              "Karnataka",            12.2958,    76.6394),
    ("Hubli",               "Karnataka",            15.3647,    75.1240),
    ("Mangalore",           "Karnataka",            12.9141,    74.8560),
    ("Kozhikode",           "Kerala",               11.2588,    75.7804),
    ("Warangal",            "Telangana",            17.9784,    79.5941),
    ("Guntur",              "Andhra Pradesh",       16.3067,    80.4365),
    ("Allahabad",           "Uttar Pradesh",        25.4358,    81.8463),
    ("Siliguri", "West Bengal", 26.7271, 88.3953),
]



NEW_EDGES = [
    ("Delhi",           "Ludhiana"          ),
    ("Delhi",           "Amritsar"          ),
    ("Delhi",           "Dehradun"          ),
    ("Jaipur",          "Ahmedabad"         ),
    ("Jaipur",          "Indore"            ),
    ("Mumbai",          "Ahmedabad"         ),
    ("Mumbai",          "Hyderabad"         ),
    ("Mumbai",          "Bangalore"         ),
    ("Pune",            "Bangalore"         ),
    ("Pune",            "Hyderabad"         ),
    ("Ahmedabad",       "Indore"            ),
    ("Indore",          "Nagpur"            ),
    ("Indore",          "Hyderabad"         ),
    ("Nagpur",          "Hyderabad"         ),
    ("Nagpur",          "Vijayawada"        ),
    ("Bhopal",          "Nagpur"            ),
    ("Lucknow",         "Allahabad"         ),
    ("Varanasi",        "Allahabad"         ),
    ("Visakhapatnam",   "Hyderabad"         ),
    ("Visakhapatnam",   "Chennai"           ),
    ("Bangalore",       "Kochi"             ),
    ("Hyderabad",       "Pune"              ),
    ("Dehradun",        "Delhi"             ),
    ("Amritsar",        "Delhi"             ),
    ("Ludhiana",        "Delhi"             ),
    ("Chandigarh",      "Jaipur"            ),
    ("Agra",            "Gwalior"           ),
    ("Kolkata",         "Visakhapatnam"     ),
    ("Bhubaneswar",     "Visakhapatnam"     ),
    ("Patna","Siliguri"),
    ("Kolkata", "Siliguri"),
    ("Siliguri", "Guwahati"),
    ("Ranchi", "Siliguri"),
    ("Ranchi",          "Visakhapatnam"     ),
    ("Nagpur",          "Raipur"            ),
    ("Allahabad",       "Patna"             ),
    ("Allahabad",       "Kanpur"            ),
]


class Command(BaseCommand):
    help = 'Seeds cities and edges with real OSRM distances'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding cities...")
        city_map = {}

        for name, state, lat, lng in CITIES:
            city, created = City.objects.get_or_create(
                name=name,
                defaults={
                    'state'    : state,
                    'latitude' : lat,
                    'longitude': lng,
                }
            )
            city_map[name] = city
            status = "created" if created else "exists"
            self.stdout.write(f"  {name} — {status}")

        self.stdout.write("\nSeeding new edges with OSRM distances...")

        for from_name, to_name in NEW_EDGES:
            from_city = city_map.get(from_name)
            to_city   = city_map.get(to_name)

            if not from_city or not to_city:
                self.stdout.write(f"  SKIP — city not found: {from_name} or {to_name}")
                continue

            already_exists = Edge.objects.filter(
                from_city=from_city, to_city=to_city
            ).exists() or Edge.objects.filter(
                from_city=to_city, to_city=from_city
            ).exists()

            if already_exists:
                self.stdout.write(f"  SKIP — already exists: {from_name} ↔ {to_name}")
                continue

            distance = get_osrm_distance(from_city, to_city)

            if distance is None:
                self.stdout.write(f"  FAIL — OSRM error: {from_name} ↔ {to_name}")
                continue

            Edge.objects.create(
                from_city   = from_city,
                to_city     = to_city,
                distance_km = distance,
            )
            self.stdout.write(f"  OK — {from_name} ↔ {to_name}: {distance} km")
            time.sleep(1)

        self.stdout.write(self.style.SUCCESS("\nDone."))