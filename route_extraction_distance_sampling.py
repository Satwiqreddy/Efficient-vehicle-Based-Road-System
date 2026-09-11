"""
Adds REAL distance-based sampling to route waypoints, since the
existing decode_polyline() samples every Nth raw polyline point --
not every N meters. Road curves have more points, straight stretches
have fewer, so "interval=10" doesn't mean a consistent real-world
distance.

This walks the full-resolution polyline and picks a new point only
once at least `meters` of real distance has passed since the last
one picked -- giving you genuinely consistent spacing.

Usage:
    from route_extraction.polyline_parser import decode_polyline_by_distance
    waypoints = decode_polyline_by_distance(polyline_str, meters=30)
"""

import math
import polyline


def haversine_meters(lat1, lng1, lat2, lng2):
    """Same formula as routing_engine/astar.py's haversine, but in meters not km."""
    R = 6371000  # meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def decode_polyline_by_distance(polyline_str, meters=30):
    """
    Decodes the polyline and samples one point approximately every
    `meters` of real distance along the route, regardless of how
    densely Google encoded that stretch of road.
    """
    all_points = polyline.decode(polyline_str)

    if not all_points:
        return []

    sampled = [all_points[0]]
    last_lat, last_lng = all_points[0]

    for lat, lng in all_points[1:]:
        distance = haversine_meters(last_lat, last_lng, lat, lng)
        if distance >= meters:
            sampled.append((lat, lng))
            last_lat, last_lng = lat, lng

    # Always include the actual endpoint, even if it's closer than `meters`
    # to the last sampled point -- otherwise the route could end short.
    if sampled[-1] != all_points[-1]:
        sampled.append(all_points[-1])

    return sampled
