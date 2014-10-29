# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Forms for the Imgin application
# (c) Twined/Univers 2009-2013. All rights reserved.
# ----------------------------------------------------------------------

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from .models import BaseImageSeries, BaseImageCategory
from cerebrum.fields import SlugField


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
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            SlugField('slug'),
            'credits',
        )
        self.helper.add_input(
            Submit('submit', 'Lagre', css_class="btn btn-primary"))

        super(BaseImageSeriesForm, self).__init__(*args, **kwargs)

    def clean_slug(self):
        data = self.cleaned_data['slug']

        if not self.has_changed():
            return data

        if 'slug' not in self.changed_data:
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
