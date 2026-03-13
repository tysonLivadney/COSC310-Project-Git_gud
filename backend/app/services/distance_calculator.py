from math import radians, sin, cos, sqrt, atan2
from schemas.location import Location

class DistanceCalculator:
    EARTH_RADIUS_IN_KM = 6371.0
    @staticmethod
    def calculate_distance_km(from_location: Location, to_location: Location) -> float:
        lat1 = radians(from_location.latitude)
        lon1 = radians(from_location.longitude)
        lat2 = radians(to_location.latitude)
        lon2 = radians(to_location.longitude)
        dis_lat = lat2 - lat1
        dis_lon = lon2 - lon1
        a = sin(dis_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dis_lon/2) ** 2
        b = 2 * atan2(sqrt(a),sqrt(1-a))
        return DistanceCalculator.EARTH_RADIUS_IN_KM * b