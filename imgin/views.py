# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Generic Base Views for the Imgin application
# (c) Twined/Univers 2009-2013. All rights reserved.
# ----------------------------------------------------------------------

import json

from django.contrib import messages
from django.http import HttpResponse
from django.utils.text import slugify
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic import View

from cerebrum.mixins import DispatchProtectionMixin
from cerebrum.mixins import CsrfExemptMixin
from cerebrum.mixins import FormMessagesMixin

from .forms import BaseImageCategoryForm
from .forms import BaseImageSeriesForm

from .models import BaseFrontpageImage
from .models import BaseImage
from .models import BaseImageCategory
from .models import BaseImageSeries


# - Extendable Generic Views -------------------------------------------


class BaseView(View):
    """
    Extends View with `model` context referring to self.model
    """
    model = BaseImage

    def get_context_data(self, **kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)
        context['model'] = self.model
        return context


class BaseTemplateView(TemplateView):
    """
    Extends TemplateView with `model` context referring to self.model
    """
    model = BaseImage

    def get_context_data(self, **kwargs):
        context = super(BaseTemplateView, self).get_context_data(**kwargs)
        context['model'] = self.model
        return context


class BaseListView(ListView):
    """
    Extends ListView with `model` context referring to self.model
    """
    model = BaseImage

    def get_context_data(self, **kwargs):
        context = super(BaseListView, self).get_context_data(**kwargs)
        context['model'] = self.model
        return context


class BaseUpdateView(UpdateView):
    """
    Extends UpdateView with `model` context referring to self.model
    """
    model = BaseImage

    def get_context_data(self, **kwargs):
        context = super(BaseUpdateView, self).get_context_data(**kwargs)
        context['model'] = self.model
        return context


class BaseCreateView(CreateView):
    """
    Extends CreateView with `model` context referring to self.model
    """
    model = BaseImage

    def get_context_data(self, **kwargs):
        context = super(BaseCreateView, self).get_context_data(**kwargs)
        context['model'] = self.model
        return context

# - BaseImage views ----------------------------------------------------


class BaseImageCreateView(DispatchProtectionMixin, BaseTemplateView):
    """
    Displays upload form. Previously uploaded images are available
    as `images` in template.
    """
    model = BaseImage
    template_name = 'imgin/admin/baseimage_create.html'

    def get_context_data(self, **kwargs):
        context = super(BaseImageCreateView, self).get_context_data(**kwargs)
        context['images'] = self.model.objects.all()

        return context


class AJAXBaseImageHandleUploadView(BaseView):
    """
    Handles upload post() from BaseImageCreateView().
    Called through AJAX
    """
    model = BaseImage

    def post(self, request, *args, **kwargs):
        image = self.model()
        return HttpResponse(image.handle_upload(request, *args, **kwargs))


class BaseImageListView(ListView):
    """
    Lists all images.
    """
    model = BaseImage
    context_object_name = 'images'
    template_name = 'imgin/admin/baseimage_list.html'

    def get_context_data(self, **kwargs):
        context = super(BaseImageListView, self).get_context_data(**kwargs)
        context['model'] = self.model
        return context


class AJAXBaseImageDeleteView(BaseView):
    """
    AJAX: Delete image by `id`
    returns a dict of `status` and `id` of deleted image
    """
    model = BaseImage

    def post(self, request, *args, **kwargs):
        if not request.POST.get('id'):
            return json.dumps({
                'status': 500,
                'error_msg': 'No ID supplied!'
            })

        photo_id = request.POST['id']
        f = self.model.objects.get(pk=photo_id)
        f.delete()

        return HttpResponse(json.dumps({
            'status': 200,
            'id': photo_id
        }), content_type="application/json")


class AJAXBaseImageDeleteMultipleView(BaseView):
    """
    AJAX: Delete image by `ids`
    returns a dict of `status` and `ids` of deleted image
    """
    model = BaseImage

    def post(self, request, *args, **kwargs):
        if not request.POST.get('ids'):
            return json.dumps({
                'status': 500,
                'error_msg': 'No IDs supplied!'
            })

        ids = request.POST['ids'].split(',')
        for image_id in ids:
            img = self.model.objects.get(pk=image_id)
            img.delete()

        return HttpResponse(json.dumps({
            'status': 200,
            'ids': ids
        }), content_type="application/json")


class AJAXBaseImageListView(BaseView):
    """
    AJAX: Returns a JSON object of all images with thumb and large size urls
    """
    model = BaseImage

    def get(self, request, *args, **kwargs):
        images = [
            {
                "thumb": image.url_s(),
                "image": image.url_l()
            } for image in self.model.objects.all().order_by("-created")
        ]
        return HttpResponse(
            json.dumps(images), content_type="application/json")


class AJAXBaseImageSortView(BaseView):
    """
    AJAX: Sorts images from a list of `id`s supplied through POST.
    """
    model_to_sort = BaseImage

    def post(self, request, *args, **kwargs):
        if not request.POST['ids']:
            return json.dumps({
                'status': 500,
                'error_msg': 'No IDs supplied!'
            })

        ids = request.POST['ids'].split(',')

        ordered_list = map(list, zip(ids, range(len(ids))))

        for image_id, order in ordered_list:
            f = self.model_to_sort.objects.get(id=image_id)
            f.order = order
            f.save()

        return HttpResponse(json.dumps({
            'status': 200,
        }), content_type="application/json")

# - BaseImageCategory views --------------------------------------------


class BaseImageCategoryListView(BaseListView):
    """
    Lists all `ImageCategory` objects
    """
    model = BaseImageCategory
    context_object_name = "image_categories"
    template_name = "imgin/admin/baseimagecategory_list.html"


class BaseImageCategoryCreateView(BaseCreateView):
    """
    Displays form and handles creation of `ImageCategory`
    """
    model = BaseImageCategory
    form_class = BaseImageCategoryForm
    form_valid_message = "Lagret kategori"
    form_invalid_message = "Rett feilene under"
    template_name = "imgin/admin/baseimagecategory_form.html"

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.name)
        form.instance.user = self.request.user
        return super(BaseImageCategoryCreateView, self).form_valid(form)


class BaseImageCategoryUpdateView(FormMessagesMixin,
                                  BaseUpdateView):
    """
    Displays form and handles updates of `ImageCategory`
    """
    model = BaseImageCategory
    form_class = BaseImageCategoryForm
    form_valid_message = "Lagret oppdatert kategori"
    form_invalid_message = "Rett feilene under"
    template_name = "imgin/admin/baseimagecategory_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BaseImageCategoryUpdateView, self).form_valid(form)


class BaseImageCategoryDeleteView(DeleteView):
    """
    Confirms deletion of an `ImageCategory`
    """
    model = BaseImageCategory
    template_name = "imgin/admin/baseimagecategory_confirm_delete.html"


class BaseImageCategorySortSeriesView(TemplateView):
    """
    The end user view for sorting image series within a category
    """
    template_name = 'imgin/admin/baseimageseries_sortseries.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BaseImageCategorySortSeriesView,
                        self).get_context_data(**kwargs)

        category = self.model.objects.get(pk=self.kwargs['category_id'])
        context['category'] = category
        return context


class AJAXBaseImageCategorySortSeriesUpdate(CreateView):
    """
    AJAX: Sorts imageseries within a category
    """
    model = BaseImageSeries

    def post(self, request, *args, **kwargs):
        if not request.POST['ids']:
            return json.dumps({
                'status': 500,
                'error_msg': 'No IDs supplied!'
            })

        ids = request.POST['ids'].split(',')

        ordered_list = map(list, zip(ids, range(len(ids))))

        for image_id, order in ordered_list:
            f = self.model.objects.get(id=image_id)
            f.order = order
            f.save()

        return HttpResponse(json.dumps({
            'status': 200,
        }), content_type="application/json")

# - BaseImageSeries views --------------------------------------------


class BaseImageSeriesListView(BaseListView):
    model = BaseImageSeries
    context_object_name = "imageseries"
    categories_object = None
    template_name = "imgin/admin/baseimageseries_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(
            BaseImageSeriesListView, self).get_context_data(**kwargs)
        context['image_categories'] = self.categories_object

        return context


class BaseImageSeriesCreateView(FormMessagesMixin,
                                BaseCreateView):

    model = BaseImageSeries
    form_class = BaseImageSeriesForm
    form_valid_message = "Bildeserie opprettet"
    form_invalid_message = "Rett feilene under"
    template_name = "imgin/admin/baseimageseries_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.slug = slugify(form.instance.name)
        form.instance.order = 0
        return super(BaseImageSeriesCreateView, self).form_valid(form)


class BaseImageSeriesUpdateView(FormMessagesMixin,
                                DispatchProtectionMixin,
                                BaseUpdateView):

    model = BaseImageSeries
    form_class = BaseImageSeriesForm
    form_valid_message = "Bildeserie oppdatert"
    form_invalid_message = "Rett feilene under"
    series_id_attr_name = 'image_series_id'
    template_name = "imgin/admin/baseimageseries_update.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(
            BaseImageSeriesUpdateView, self
        ).get_context_data(**kwargs)

        image_series = self.model.objects.get(
            pk=self.kwargs[self.series_id_attr_name])
        context['image_series'] = image_series
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BaseImageSeriesUpdateView, self).form_valid(form)


class BaseImageSeriesAddImagesView(DispatchProtectionMixin, TemplateView):
    model = BaseImageSeries
    related_images = 'related_images'
    template_name = 'imgin/admin/baseimageseries_add_images.html'
    series_id_attr_name = 'image_series_id'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(
            BaseImageSeriesAddImagesView, self
        ).get_context_data(**kwargs)

        image_series = self.model.objects.get(
            pk=self.kwargs[self.series_id_attr_name])
        context['images'] = getattr(image_series,
                                    self.related_images).all()
        context['image_series'] = image_series
        return context


class AJAXBaseImageSeriesDeleteView(BaseView):
    '''
    AJAX: Sorts imageseries within a category
    '''
    model = BaseImageSeries

    def post(self, request, *args, **kwargs):
        if not request.POST['pk']:
            return json.dumps({
                'status': 500,
                'error_msg': 'No ID supplied!'
            })

        series = self.model.objects.get(pk=request.POST['pk'])

        series.delete()

        return HttpResponse(json.dumps({
            'status': 200,
            'id': "#series-%s" % request.POST['pk']
        }), content_type="application/json")


# - Frontpage Views ----------------------------------------------------


class BaseFrontpageListView(TemplateView):
    model = BaseFrontpageImage
    image_source_model = BaseImage
    template_name = 'imgin/admin/basefrontpageimage_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BaseFrontpageListView, self).get_context_data(**kwargs)
        frontpage_images = self.model.objects.all()
        frontpage_ids = [f.image_id for f in frontpage_images]
        # don't show images already on frontpage.
        images = self.image_source_model.objects.all().exclude(
            id__in=frontpage_ids)
        context.update({
            'frontpage_images': frontpage_images,
            'images': images
        })
        return context


class AJAXBaseFrontpageCreateView(CreateView):
    model = BaseFrontpageImage

    def post(self, request, *args, **kwargs):
        if not request.POST['id']:
            return json.dumps({
                'status': 500,
                'error_msg': 'No ID supplied!'
            })

        photo_id = request.POST['id']
        f = self.model()
        f.image_id = photo_id
        f.order = 0
        f.save()

        return HttpResponse(json.dumps({
            'status': 200,
            'id': "#image-%s" % photo_id,
            'f_id': f.pk,
        }), content_type="application/json")


class AJAXBaseFrontpageDeleteView(BaseView):
    model = BaseFrontpageImage

    def post(self, request, *args, **kwargs):
        if not request.POST['id']:
            return json.dumps({
                'status': 500,
                'error_msg': 'No ID supplied!'
            })

        photo_id = request.POST['id']
        f = self.model.objects.get(pk=photo_id)
        f.delete()

        return HttpResponse(json.dumps({
            'status': 200,
            'id': photo_id
        }), content_type="application/json")


class AJAXBaseFrontpageSortView(BaseView):
    model = BaseFrontpageImage

    def post(self, request, *args, **kwargs):
        if not request.POST['ids']:
            return json.dumps({
                'status': 500,
                'error_msg': 'No IDs supplied!'
            })

        ids = request.POST['ids'].split(',')

        ordered_list = map(list, zip(ids, range(len(ids))))

        for image_id, order in ordered_list:
            f = self.model.objects.get(image_id=image_id)
            f.order = order
            f.save()

        return HttpResponse(json.dumps({
            'status': 200,
        }), content_type="application/json")

# - CKEDITOR view ------------------------------------------------------


class BaseCKEDITORBrowserView(BaseListView):
    model = BaseImage
    context_object_name = "images"
    template_name = 'imgin/admin/baseckeditor_browser_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BaseCKEDITORBrowserView,
                        self).get_context_data(**kwargs)
        context['func_num'] = self.request.GET.get('CKEditorFuncNum')
        return context


# - FroalaJson view ------------------------------------------------------


class BaseAJAXFroalaBrowserView(BaseListView):
    model = BaseImage
    context_object_name = "images"
    template_name = 'imgin/admin/basefroala_browser_list.html'

    def get(self, request, *args, **kwargs):
        image_list = []
        images = self.model.objects.all()

        for image in images:
            image_list.append({
                'src': image.url_t,
                'info': {
                    'target': image.url_l,
                }
            })

        return HttpResponse(json.dumps(image_list),
                            content_type="application/json")


class BaseAJAXFroalaUploadView(CsrfExemptMixin, BaseView):
    model = BaseImage

    def post(self, request, *args, **kwargs):
        image = self.model()
        return HttpResponse(
            image.handle_froala_upload(request, *args, **kwargs)
        )


# - Misc Utility views -------------------------------------------------


class BaseRecreateThumbnailsView(BaseView):
    model = BaseImage

    def get(self, request, *args, **kwargs):
        raise NotImplemented()
