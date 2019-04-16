from os import path


# Model Utility Functions

def user_profile_img_dir(instance, filename):
    return path.join('people', instance.email,
                     'profile_images', filename)


# View Utility Functions

def clear_previous_ministry_login(request, user, *args, **kwargs):
    """ Automatically clears alias of last MinistryProfile alias.
    """
    user.logged_in_as = None
    user.save()
