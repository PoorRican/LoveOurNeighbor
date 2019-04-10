from django.db import models

from pickle import loads, dumps
from geopy import Nominatim, distance


gc = Nominatim(user_agent="LoveOurNeighbor")


def calc_distance(request, ministry_location, units='miles'):
    """ Calculate the distance between user and ministry.

    In the current implementation this is very inefficient and not scalable.
    The solution is to store the coordinates of the ministry ahead of time.
    """
    location = None
    if request.user.location:
        location = request.user.location.location
    else:
        # TODO: calculate location via IP or other API
        pass

    _ml = ministry_location.location
    if location and _ml:

        dist = distance.distance(location, _ml)

        if units == 'miles':
            return dist.miles

        elif units == 'km':
            return dist.km

        else:
            raise ValueError('Unknown unit of length passed')

    else:   # if there is location of either User or MinistryProfile
        return 0


class GeoLocation(models.Model):
    _location = models.BinaryField(max_length=1024)
    user = models.OneToOneField('people.User',
                                null=True, blank=True,
                                on_delete=models.CASCADE)
    ministry = models.OneToOneField('ministry.MinistryProfile',
                                    null=True, blank=True,
                                    on_delete=models.CASCADE)
    # TODO: somehow prevent simultaneous `user` and `ministry` fields

    @property
    def location(self):
        if self._location:
            return loads(self._location)
        else:
            return None

    @location.setter
    def location(self, location):
        if type(location) is str:
            _, L = gc.geocode(location)
            self._location = dumps(L)
        else:
            raise TypeError("location argument is not of type str")
