IMGIN
=====

**NOTE: This is tailored for the twined project structure,
it probably won't work too well without customization on other
project bootstraps.**

Installation:
-------------

    pip install -e git://github.com/twined/imgin.git#egg=imgin-dev


Usage:
------

Base models:

  - class BaseFrontpageImage(models.Model):
  - class BaseImageCategory(models.Model):
  - class BaseImageSeries(models.Model):
  - class BaseImage(models.Model):


**BaseImage views:**

    class BaseImageCreateView(BaseTemplateView):
        model = BaseImage
        template_name = ''


    class AJAXBaseImageHandleUploadView(BaseView):
        model = BaseImage


    class BaseImageListView(ListView):
        model = BaseImage
        context_object_name = 'images'
        template_name = ''


    class AJAXBaseImageDeleteView(BaseView):
        model = BaseImage


    class AJAXBaseImageListView(BaseView):
        model = BaseImage


    class AJAXBaseImageSortView(BaseView):
        model_to_sort = BaseImage
