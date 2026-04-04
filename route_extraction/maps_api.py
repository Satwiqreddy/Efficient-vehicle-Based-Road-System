import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_route(origin, destination):
    """
    Fetches route polyline from Google Directions API.
    Returns decoded waypoints as list of (lat, lng) tuples.
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] != "OK":
        raise Exception(f"Directions API error: {data['status']}")

    # Extract the encoded polyline from the route
    polyline_str = data["routes"][0]["overview_polyline"]["points"]
    return polyline_str


if __name__ == "__main__":
    origin = "Kurnool, Andhra Pradesh"
    destination = "Hyderabad, Telangana"
    polyline = get_route(origin, destination)
    print("Polyline received:")
    print(polyline[:80], "...")