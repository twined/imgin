# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Utils for the Imgin application
# (c) Twined/Univers 2009-2013. All rights reserved.
# ----------------------------------------------------------------------


import errno
import os
import re
import types
import logging

from cStringIO import StringIO as BufferIO
from PIL import Image, ImageFile

from .helpers import ImginError


logger = logging.getLogger(__name__)
geometry_pat = re.compile(r'^(?P<x>\d+)?(?:x(?P<y>\d+))?$')


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

    cropped_image = cropped.copy()
    if cropped.size[0] > width or cropped.size[1] > height:
        cropped_image = cropped.resize(size=(width, height),
                                       resample=Image.ANTIALIAS)
    return cropped_image


def get_thumbnail(file_, geometry_string, **options):
    """
    Returns thumbnail as an ImageFile instance for file with geometry and
    options given. First it will try to get it from the key value store,
    secondly it will create it.
    """
    logger.debug('Getting thumbnail for file [%s] at [%s]' % (file_,
                 geometry_string))
    if file_:
        try:
            with open(str(file_.file.name), 'rb') as f:
                source_image = Image.open(f)
                thumbnail = source_image.copy()
        except IOError:
            raise ImginError('Could not open source image %s' % file_)
    else:
        return None

    # copy image in memory to thumbnail
    thumbnail = source_image.copy()
    image_info = get_image_info(source_image)
    options['image_info'] = image_info

    return create_thumbnail(file_, thumbnail, geometry_string, options)


def create_thumbnail(source_file, thumb, geometry_string, options):
    """
    Creates a thumbnail
    """
    logger.debug('Creating thumbnail of file [%s] at [%s] with [%s]',
                 source_file.file.name, geometry_string, options)

    ratio = get_image_ratio(thumb, options)
    geometry = parse_geometry(geometry_string, ratio)
    if not options.get('crop') is '':
        image = smart_crop(thumb, geometry[0], geometry[1], **options)
    else:
        image = scale(thumb, geometry, options)

    return image


def write_image(image, options, thumbnail):
    """
    Wrapper for ``_write``
    """
    format_ = options['format']
    quality = options['quality']
    image_info = options.get('image_info', {})
    # additional non-default-value options:
    progressive = False
    raw_data = _get_raw_data(
        image, format_, quality,
        image_info=image_info,
        progressive=progressive
    )
    thumbnail.write(raw_data)


def _get_raw_data(image, format_, quality, image_info=None, progressive=False):
    # Increase (but never decrease) PIL buffer size
    ImageFile.MAXBLOCK = max(ImageFile.MAXBLOCK, image.size[0] * image.size[1])
    bf = BufferIO()

    params = {
        'format': format_,
        'quality': quality,
        'optimize': 1,
    }

    # keeps icc_profile
    if 'icc_profile' in image_info:
        params['icc_profile'] = image_info['icc_profile']

    raw_data = None

    if format_ == 'JPEG' and progressive:
        params['progressive'] = True
    try:
        # Do not save unnecessary exif data for smaller thumbnail size
        params.pop('exif', {})
        image.save(bf, **params)
    except (IOError, OSError):
        # Try without optimization.
        params.pop('optimize')
        image.save(bf, **params)
    else:
        raw_data = bf.getvalue()
    finally:
        bf.close()

    return raw_data


def _calculate_scaling_factor(x_image, y_image, geometry, options):
    crop = options['crop']
    factors = (geometry[0] / x_image, geometry[1] / y_image)
    return max(factors) if crop else min(factors)


def scale(image, geometry, options):
    """
    Scales image before returning it.
    """
    upscale = options['upscale']
    x_image, y_image = map(float, get_image_size(image))
    factor = _calculate_scaling_factor(x_image, y_image, geometry, options)

    if factor < 1 or upscale:
        width = toint(x_image * factor)
        height = toint(y_image * factor)
        image = image.resize((width, height), resample=Image.ANTIALIAS)

    return image


def get_image(source):
    # use Image.open(source)
    return


def get_image_size(image):
    return image.size


def get_image_info(image):
    return image.info or {}


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


def get_image_ratio(image, options):
        """
        Calculates the image ratio. If cropbox option is used, the ratio
        may have changed.
        """
        x, y = image.size

        return float(x) / y


def parse_geometry(geometry, ratio=None):
    """
    Parses a geometry string syntax and returns a (width, height) tuple
    """
    m = geometry_pat.match(geometry)

    def syntax_error():
        raise ImginError('Geometry does not have the correct '
                         'syntax: %s' % geometry)

    if not m:
        raise syntax_error()
    x = m.group('x')
    y = m.group('y')
    if x is None and y is None:
        raise syntax_error()
    if x is not None:
        x = int(x)
    if y is not None:
        y = int(y)
        # calculate x or y proportionally if not set but we need the image ratio
    # for this
    if ratio is not None:
        ratio = float(ratio)
        if x is None:
            x = toint(y * ratio)
        elif y is None:
            y = toint(x / ratio)
    return x, y
