from django import forms

from .models import MinistryProfile


class MinistryEditForm(forms.ModelForm):
    """Form for viewing and editing fields in a MinistryProfile object.

    A good reference for Django forms is:
    http://pydanny.com/core-concepts-django-modelforms.html
    """
    tags = forms.CharField(max_length=256, required=False)
    reps = forms.CharField(max_length=1024, required=False)

    def __init__(self, *args, **kwargs):
        super(MinistryEditForm, self).__init__(*args, **kwargs)

    class Meta:
        model = MinistryProfile
        fields = ('profile_img', 'banner_img',
                  'name', 'address', 'phone_number', 'website', 'founded',
                  'facebook', 'instagram', 'youtube', 'twitter',
                  'admin', 'description', 'staff',)
        exclude = ('admin',)
        widgets = {'description': forms.Textarea(attrs={'rows': 20,
                                                        'cols': 80}),
                   'address': forms.Textarea(attrs={'rows': 3,
                                                    'cols': 30,
                                                    'class': 'materialize-textarea'}),
                   'founded': forms.TextInput(attrs={'class': 'datepicker'}),
                   }
        labels = {'img_path': 'Banner Image',
                  'founded': 'Date Founded',
                  'reps': 'Representatives',
                  'phone_number': 'Phone',
                  }
