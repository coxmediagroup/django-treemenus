"""This module provides forms for editing models in the treemenus package."""

from django import forms
from django.forms.util import ErrorList

from treemenus.models import Menu

class MenuForm(forms.ModelForm):
    """This is the form for editing a Menu model"""

    def __init__(self, *args, **kwargs):
        super(MenuForm, self).__init__(*args, **kwargs)
        self.fields['originating_site'].required = True

    class Meta:
        "Ceci n'est pas une docstring"

        model = Menu
        fields = [ 'name', 'originating_site', 'sites' ]
