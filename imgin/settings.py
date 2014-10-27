# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Settings for the Imgin application
# (c) Twined/Univers 2009-2013. All rights reserved.
# ----------------------------------------------------------------------

import os

from django.conf import settings

from .utils import merge_settings

IMGIN_CONFIG = {
    'base': {},
    'portfolio': {
        'allowed_exts': [".jpg", ".png", ".jpeg",
                         ".JPG", ".PNG", ".JPEG"],
        'belongs_to': 'ImageSeries',
        'default_map': 'l',
        'upload_dir': os.path.join('images', 'portfolio'),
        'size_limit': 10240000,
        'size_map': {
            'l': {
                'landscape': 'x600',
                'portrait': 'x600',
                'dir': 'l',
                'class_name': 'large',
                'crop': '',
                'quality': 100,
                'format': 'PNG',
            },
            'm': {
                'landscape': 'x310',
                'portrait': 'x310',
                'dir': 'm',
                'class_name': 'medium',
                'crop': '',
                'quality': 100,
                'format': 'PNG',
            },
            's': {
                'landscape': 'x200',
                'portrait': 'x200',
                'dir': 's',
                'class_name': 'small',
                'crop': '',
                'quality': 100,
                'format': 'PNG',
            },
            't': {
                'landscape': '140x140',
                'portrait': '140x140',
                'dir': 't',
                'class_name': 'thumb',
                'crop': 'center',
                'quality': 100,
                'format': 'PNG',
            },
        },
    },
}

IMGIN_CONFIG = merge_settings(
    IMGIN_CONFIG,
    getattr(settings, 'IMGIN_CONFIG', {})
)
