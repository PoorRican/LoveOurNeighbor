from geopy import distance
from requests import get
from json import loads
from ipware import get_client_ip

from .models import gc


def calc_distance(request, ministry_location, units='miles') -> int:
    """ Calculate the distance between user and ministry.

    In the current implementation this is very inefficient and not scalable.
    The solution is to store the coordinates of the ministry ahead of time.

    Parameters
    ----------
    request: Request
        django request object

    ministry_location: (str)
        GeoLocation

    units: (str)
        Can either be 'miles' or 'km' and defines the units to return
    """
    location = None
    if request.user.location:
        location = request.user.location.location
    else:
        client_ip, is_routable = get_client_ip(request)
        if client_ip is not None and is_routable:
            _, location = gc.geocode(get_location_from_ip(client_ip)['zip_code'])

    if location and ministry_location:

        dist = distance.distance(location, ministry_location.location)

        if units == 'miles':
            return dist.miles

        elif units == 'km':
            return dist.km

        else:
            raise ValueError('Unknown unit of length passed')

    else:   # if there is location of either User or MinistryProfile
        return 0


def get_location_from_ip(ip: str):
    """
    Performs geolocation via http://freegeoip.live API.


    Parameters
    ----------
    ip (str):
        IP address to look up

    Returns
    -------
    GeoLocationInfo
        containing location data returned by API

    See Also
    --------
    GeoLocationInfo for possible return dict keys
    """
    # TODO: check if `ip` is valid IP address
    url = 'http://freegeoip.live/json/%s'
    r = get(url % ip)
    return loads(r.content)
