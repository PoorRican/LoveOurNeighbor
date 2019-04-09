from django.db import models

from geopy import Nominatim, distance


gc = Nominatim(user_agent="LoveOurNeighbor")


def calc_distance(request, address, units='miles'):
    """ Calculate the distance between user and ministry.

    In the current implementation this is very inefficient and not scalable.
    The solution is to store the coordinates of the ministry ahead of time.
    """
    location = None
    if request.user.location:
        _, location = gc.geocode(request.user.location)
    else:
        # TODO: calculate location via IP or other API
        pass

    if location and address:
        _, ministry_location = gc.geocode(address)

        dist = distance.distance(location, ministry_location)

        if units == 'miles':
            return dist.miles

        elif units == 'km':
            return dist.km

        else:
            raise ValueError('Unknown unit of length passed')

    else:   # if there is location of either User or MinistryProfile
        return 0
