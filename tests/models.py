import os

from django.core.urlresolvers import reverse
from django.db import models
from imgin.models import BaseImage
from imgin.models import BaseImageSeries


class PfSeries(BaseImageSeries):
    @staticmethod
    def get_create_url():
        return reverse(
            'series-create'
        )

    def get_update_url(self):
        return reverse(
            'series-update',
            kwargs={'pk': self.pk}
        )

    def get_addimages_url(self):
        return reverse(
            'series-addimages',
            kwargs={'image_series_id': self.pk}
        )

    def get_upload_url(self):
        return reverse(
            'series-upload',
            kwargs={'image_series_id': self.pk}
        )

    def get_absolute_url(self):
        return reverse(
            'series-list',
            kwargs={
                'pk': self.pk,
            }
        )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Bildeserie'
        verbose_name_plural = 'Bildeserier'
        ordering = ['order', '-created']


class PfImage(BaseImage):
    IMGIN_CFG = {
        'allowed_exts': [".jpg", ".png", ".jpeg",
                         ".JPG", ".PNG", ".JPEG"],
        'belongs_to': 'ImageSeries',
        'default_map': 'medium',
        'upload_dir': os.path.join('images'),
        'size_limit': 10240000,
        'size_map': {
            'large': {
                'landscape': 'x600',
                'portrait': 'x600',
                'dir': 'large',
                'class_name': 'large',
                'crop': '',
                'quality': 100,
                'format': 'original',
                'media_queries': (
                    ['retina'],
                )
            },
            'medium': {
                'landscape': 'x310',
                'portrait': 'x310',
                'dir': 'medium',
                'class_name': 'medium',
                'crop': '',
                'quality': 100,
                'format': 'original',
                'media_queries': (
                    ['desktop'],
                )
            },
            'small': {
                'landscape': 'x200',
                'portrait': 'x200',
                'dir': 'small',
                'class_name': 'small',
                'crop': '',
                'quality': 100,
                'format': 'original',
                'media_queries': (
                    ['mobile'],
                )
            },
            'thumb': {
                'landscape': '140x140',
                'portrait': '140x140',
                'dir': 'thumb',
                'class_name': 'thumb',
                'crop': 'center',
                'quality': 100,
                'format': 'original',
            },
        },
    }

    series = models.ForeignKey(PfSeries, related_name='related_images',
                               null=True, blank=True)

    def get_upload_url(self):
        return '/'

    def get_create_url(self):
        return '/'

    class Meta:
        app_label = 'tests'
