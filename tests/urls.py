from django.conf.urls import include, patterns, url

from .views import (
    ImageCreateView, ImageListView, ImageSeriesRecreateThumbnailsView,
    ImageSeriesListView, ImageSeriesCreateView, ImageSeriesUpdateView
)

urlpatterns = patterns(
    '',
    # url(r'^admin/', include('cerebrum.admin.admin_urls')),
    url(r'^image-create-view/$', ImageCreateView.as_view(),
        name='image-create'),
    url(r'^image-list-view/$', ImageListView.as_view(),
        name='image-list'),

    # imageseries
    url(r'^imageseries-recreate-thumbnails-view/$',
        ImageSeriesRecreateThumbnailsView.as_view(),
        name="series-recreate"),
    url(r'^imageseries-recreate-thumbnails-view/(?P<image_series_id>\d+)$',
        ImageSeriesRecreateThumbnailsView.as_view(),
        name="series-recreate"),
    url(r'^imageseries-list-view/(?P<pk>\d+)$',
        ImageSeriesListView.as_view(),
        name="series-list"),
    url(r'^imageseries-create-view/$',
        ImageSeriesCreateView.as_view(),
        name="series-create"),
    url(r'^imageseries-update-view/(?P<pk>\d+)$',
        ImageSeriesUpdateView.as_view(),
        name="series-update"),
)
