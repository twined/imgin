from django.conf.urls import patterns, url

from .views import ImageCreateView, ImageListView

urlpatterns = patterns(
    '',
    url(r'^image-create-view/$', ImageCreateView.as_view(),
        name='image-create'),
    url(r'^image-list-view/$', ImageListView.as_view(),
        name='image-list'),
)
