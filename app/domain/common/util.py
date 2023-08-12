import math
from typing import Tuple


class GeoLocationHelper:
    EARTH_RADIUS = 6371
    MIN_LAT = math.radians(-90)
    MAX_LAT = math.radians(90)
    MIN_LON = math.radians(-180)
    MAX_LON = math.radians(180)

    @staticmethod
    def calculate_bounding_box(
        latitude: float, longitude: float, distance: int
    ) -> Tuple[float, float, float, float]:
        """
        latitude : latitude in degrees
        longitude : longitude in degrees
        distance : max distance between points
        Returns:
            Tuple(latitude_min, latitude_max, longitude_min, longitude_max)
            note: returns are also in degrees
        """
        lat = math.radians(latitude)
        lon = math.radians(longitude)
        r = distance / GeoLocationHelper.EARTH_RADIUS  # angular radius of the query circle
        # calculating the latitude is easy, just +- r
        lat_min, lat_max = lat - r, lat + r

        if lat_min > GeoLocationHelper.MIN_LAT and lat_max < GeoLocationHelper.MAX_LAT:
            delta_lon = math.asin(math.sin(r) / math.cos(lat))

            lon_min = lon - delta_lon
            if lon_min < GeoLocationHelper.MIN_LON:
                lon_min += 2 * math.pi

            lon_max = lon + delta_lon
            if lon_max > GeoLocationHelper.MAX_LON:
                lon_max -= 2 * math.pi
        # if we didn't land in the first if statement,
        # we hit the poles, fix accordingly
        else:
            lat_min = max(lat_min, GeoLocationHelper.MIN_LAT)
            lat_max = min(lat_max, GeoLocationHelper.MAX_LAT)
            lon_min = GeoLocationHelper.MIN_LON
            lon_max = GeoLocationHelper.MAX_LON

        return (
            math.degrees(lat_min),
            math.degrees(lat_max),
            math.degrees(lon_min),
            math.degrees(lon_max),
        )
