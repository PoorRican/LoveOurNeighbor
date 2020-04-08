from .models import View


def add_views(obj, num: int):
    """
    Helper function to create a certain number of views for a profile.

    An explicit number of 'anonymous' `View` objects (no `user`) are created, from today's date, pointing to `obj`.

    This was created to help transition the existing view count from when views were simply instance field
    and not relational objects. There will not be a need for this function after its first use; this will
    be deprecated in the near future...

    Parameters
    ----------
    obj:
        Object to create views for.

    num: (int)
        Number of view objects to create.

    Returns
    -------
    None
    """
    for _ in range(num):
        View.create(obj, None)
