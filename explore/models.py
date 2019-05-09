from django.db import models

from pickle import loads, dumps
from geopy import Nominatim


gc = Nominatim(user_agent="LoveOurNeighbor")


class GeoLocation(models.Model):
    _location = models.BinaryField(max_length=256)
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
            try:
                _, L = gc.geocode(location)
                self._location = dumps(L)
            except TypeError:
                raise ValueError("%s is not a valid location" % location)
        else:
            raise TypeError("location argument is not of type str")
