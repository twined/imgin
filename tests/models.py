import os
from imgin.models import BaseImage


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

    def get_upload_url(self):
        return '/'

    def get_create_url(self):
        return '/'

    class Meta:
        app_label = 'tests'
