from frontend.forms import NewProfileForm, BaseRepManagementForm, ProfileEditForm

from .models import Ministry


class NewMinistryForm(NewProfileForm):
    class Meta(NewProfileForm.Meta):
        model = Ministry


class MinistryEditForm(ProfileEditForm):
    pass


class RepManagementForm(BaseRepManagementForm):
    class Meta(BaseRepManagementForm.Meta):
        model = Ministry
