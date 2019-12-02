from os import path

from django.conf import settings


# Model Utility Functions

def user_profile_img_dir(instance, filename):
    return path.join('people', instance.email,
                     'profile_images', filename)


def verification_required():
    return not settings.REQUIRE_USER_VERIFICATION


# View Utility Functions

def clear_previous_ministry_login(request, user, *args, **kwargs):
    """ Automatically clears alias of last MinistryProfile alias.
    """
    user.logged_in_as = None
    user.save()
