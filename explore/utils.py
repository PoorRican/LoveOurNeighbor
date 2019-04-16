from geopy import distance


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
