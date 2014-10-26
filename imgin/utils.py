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


def smart_crop(img, width, height, **options):
    crop_dimensions = (width, height)
    crop_size = get_crop_size_by_scaleup(img.size, crop_dimensions)
    left = (img.size[0] - crop_size[0])/2
    top = (img.size[1] - crop_size[1])/2
    right = (img.size[0] + crop_size[0])/2
    bottom = (img.size[1] + crop_size[1])/2

    cropped = img.crop((left, top, right, bottom))

    thumbs = cropped.copy()
    if cropped.size[0] > width or cropped.size[1] > height:
        thumbs = cropped.resize(size=(width, height), **options)
    return thumbs


def get_crop_size_by_scaleup(input_dimension, scale_dimension):
    """
    From the original dimension, a target dimension is given
    Before resizing, the original image should be cropped based on the
    best scale dimension.
    """
    # If somehow, scale dimension is larger than the original size,
    # don't scale and return the original instead
    new_size = input_dimension
    if input_dimension[0] >= scale_dimension[0] or \
       input_dimension[1] >= scale_dimension[1]:
        by_width = get_size_by_width(scale_dimension, input_dimension)
        by_height = get_size_by_height(scale_dimension, input_dimension)
        if by_width[0] <= input_dimension[0] and \
           by_width[1] <= input_dimension[1]:
            new_size = by_width
        else:
            new_size = by_height
    return new_size


def get_size_by_width(input_dimension, scale_dimension):
    width = scale_dimension[0]
    # Get the height based on scaled image dimension against base width
    width_percent = (width / float(input_dimension[0]))
    height = int((float(input_dimension[1]) * float(width_percent)))
    return (width, height)


def get_size_by_height(input_dimension, scale_dimension):
    height = scale_dimension[1]
    # Get the width based on scaled image dimension against base height
    height_percent = (height / float(input_dimension[1]))
    width = int((float(input_dimension[0]) * float(height_percent)))
    return (width, height)
