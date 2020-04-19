from frontend.forms import NewProfileForm, BaseRepManagementForm, ProfileEditForm

from .models import Church


class NewChurchForm(NewProfileForm):
    class Meta(NewProfileForm.Meta):
        model = Church


class ChurchEditForm(ProfileEditForm):
    pass


class RepManagementForm(BaseRepManagementForm):
    class Meta(BaseRepManagementForm.Meta):
        model = Church
