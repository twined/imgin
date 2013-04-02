# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Utils for the Imgin application
# (c) Twined/Univers 2009-2013. All rights reserved.
# ----------------------------------------------------------------------


import errno
import os
import types

from django.conf import settings

from sorl.thumbnail import delete as sorl_delete


def merge_settings(default_settings, user_settings):
    # store a copy of default_settings, but overwrite with
    # user_settings's values where applicable
    merged = dict(default_settings, **user_settings)
    default_settings_keys = default_settings.keys()

    # if the value of merged[key] was overwritten with
    # user_settings[key]'s value then we need to put back any
    # missing default_settings[key] values
    for key in default_settings_keys:
        # if this key is a dictionary, recurse
        if isinstance(default_settings[key],
                      types.DictType) and key in user_settings:
            merged[key] = merge_settings(
                default_settings[key],
                user_settings[key]
            )

    return merged


def delete_connected_images(photo):
    sizedirs = ('l', 'm', 's',)
    for sizedir in sizedirs:
        filename = os.path.join(settings.MEDIA_ROOT, 'images', 'posts',
                                sizedir, photo.filename)
        if os.path.exists(filename):
            os.remove(filename)

    sorl_delete(photo.image)
    photo.delete()


def _mkdirs(path):
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise


def toint(number):
    """
    Helper to return rounded int for a float or just the int it self.
    """
    if isinstance(number, float):
        number = round(number, 0)
    return int(number)
