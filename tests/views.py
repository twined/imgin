from django.core.urlresolvers import reverse

from cerebrum.mixins import LoginRequiredMixin, FormMessagesMixin
from imgin.views import BaseImageCreateView, BaseImageListView
from imgin.views import (
    BaseImageSeriesRecreateThumbnailsView,
    BaseImageSeriesListView, BaseImageSeriesCreateView,
    BaseImageSeriesUpdateView, BaseUpdateView
)

from .models import PfImage, PfSeries
from .forms import PfSeriesForm


class ImageCreateView(LoginRequiredMixin, BaseImageCreateView):
    model = PfImage


class ImageListView(LoginRequiredMixin, BaseImageListView):
    model = PfImage

# imageseries


class ImageSeriesRecreateThumbnailsView(
    LoginRequiredMixin,
    BaseImageSeriesRecreateThumbnailsView
):
    model = PfSeries


class ImageSeriesListView(LoginRequiredMixin, BaseImageSeriesListView):
    model = PfSeries


class ImageSeriesCreateView(LoginRequiredMixin, BaseImageSeriesCreateView):
    model = PfSeries
    form_class = PfSeriesForm


class ImageSeriesUpdateView(FormMessagesMixin,
                            BaseUpdateView):

    model = PfSeries
    form_class = PfSeriesForm
    form_valid_message = "Bildeserie oppdatert"
    form_invalid_message = "Rett feilene under"
    series_id_attr_name = "image_series_id"
    context_object_name = "image_series"
    template_name = "imgin/admin/baseimageseries_update.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ImageSeriesUpdateView,
                        self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ImageSeriesUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'series-list',
            kwargs={'pk': self.object.pk})
