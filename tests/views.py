from imgin.views import BaseImageCreateView, BaseImageListView
from .models import PfImage


class ImageCreateView(BaseImageCreateView):
    model = PfImage


class ImageListView(BaseImageListView):
    model = PfImage
