from django.test import TestCase

from utils.test_helpers import (
    default_church_data, generate_churches,
)

from utils.profile_tests import (
    BaseProfileTestCase, BaseAggregatorTestCase,
    BaseProfileFormTestCase, TestProfileEditForm, TestRepManagementForm, TestNewProfileForm
)

from .aggregators import recent, random
from .forms import ChurchEditForm, NewChurchForm, RepManagementForm
from .models import Church


class ChurchTestCase(BaseProfileTestCase, TestCase):
    object_type = Church
    default_data_func = default_church_data


class TestChurchAggregators(BaseAggregatorTestCase, TestCase):
    default_data_func = default_church_data
    generator = generate_churches
    object_type = Church
    recent = recent
    random = random


class TestChurchForm(BaseProfileFormTestCase):
    default_data_func = default_church_data
    edit_form = ChurchEditForm
    new_form = NewChurchForm
    object_type = Church


class TestNewChurchForm(TestChurchForm, TestNewProfileForm, TestCase):
    pass


class TestChurchEditForm(TestChurchForm, TestProfileEditForm, TestCase):
    pass


class TestChurchRepManagementForm(TestRepManagementForm, TestCase):
    object_type = Church
    default_data_func = default_church_data
    rep_form = RepManagementForm
