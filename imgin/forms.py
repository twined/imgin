# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Forms for the Imgin application
# (c) Twined/Univers 2009-2013. All rights reserved.
# ----------------------------------------------------------------------

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Submit

from imgin.models import BaseImageSeries, BaseImageCategory


class BaseImageCategoryForm(forms.ModelForm):
    slug = forms.CharField(
        required=True,
        initial='slug',
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Lagre', css_class="btn btn-primary"))

        super(BaseImageCategoryForm, self).__init__(*args, **kwargs)

    class Meta:
        model = BaseImageCategory
        exclude = ('user',)


class BaseImageSeriesForm(forms.ModelForm):
    slug = forms.CharField(
        required=True,
        initial='',
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Lagre', css_class="btn btn-primary"))

        super(BaseImageSeriesForm, self).__init__(*args, **kwargs)

    def clean_slug(self):
        data = self.cleaned_data['slug']

        if not self.has_changed():
            return data

        if not 'slug' in self.changed_data:
            return data

        try:
            obj = self.Meta.model.objects.get(slug=data)
        except self.Meta.model.DoesNotExist:
            obj = None

        if isinstance(obj, self.Meta.model):
            raise forms.ValidationError(
                "Et objekt med dette navnet eksisterer allerede"
            )

        return data

    class Meta:
        model = BaseImageSeries
        exclude = ('user', 'credits', 'order',)
