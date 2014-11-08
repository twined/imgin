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
                'format': 'jpg',
            },
            'medium': {
                'landscape': 'x310',
                'portrait': 'x310',
                'dir': 'medium',
                'class_name': 'medium',
                'crop': '',
                'quality': 100,
                'format': 'jpg',
            },
            'small': {
                'landscape': 'x200',
                'portrait': 'x200',
                'dir': 'small',
                'class_name': 'small',
                'crop': '',
                'quality': 100,
                'format': 'jpg',
            },
            'thumb': {
                'landscape': '140x140',
                'portrait': '140x140',
                'dir': 'thumb',
                'class_name': 'thumb',
                'crop': 'center',
                'quality': 100,
                'format': 'jpg',
            },
        },
    }

    class Meta:
        app_label = 'tests'