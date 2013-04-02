# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Base Models for the Imgin application
# (c) Twined/Univers 2009-2013. All rights reserved.
# ----------------------------------------------------------------------

import errno
import json
import os
import uuid

from shutil import copyfile

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models

import imgin.settings

from sorl.thumbnail import (
    default, delete as sorl_delete, get_thumbnail,
    ImageField
)
from sorl.thumbnail.parsers import parse_geometry

from .utils import _mkdirs, toint
from .managers import BaseFrontpageImageManager


class BaseFrontpageImage(models.Model):
    order = models.IntegerField()

    objects = BaseFrontpageImageManager()

    class Meta:
        ordering = ['order']
        abstract = True


class BaseImageCategory(models.Model):
    '''
    Editorials/Portraits/Commercial
    '''
    name = models.CharField('Navn', max_length=50)
    slug = models.CharField('url', max_length=50)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def meta(self):
        return self._meta

    @staticmethod
    def get_create_url(*args, **kwargs):
        raise NotImplemented()

    def get_update_url(self):
        raise NotImplemented()

    def get_delete_url(self):
        raise NotImplemented()

    def get_sortseries_url(self):
        raise NotImplemented()

    @staticmethod
    def get_upload_url(*args, **kwargs):
        raise NotImplemented()

    @staticmethod
    def get_list_url(*args, **kwargs):
        raise NotImplemented()

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class BaseImageSeries(models.Model):
    '''
    A set of photos that belong together. I.E. a shoot for Vogue.
    '''
    name = models.CharField('Navn', max_length=255)
    slug = models.CharField('URL', max_length=50)
    credits = models.CharField('Krediteringer', blank=True, max_length=255)
    user = models.ForeignKey(User)
    order = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        for photo in self.related_images.all():
            photo.delete()
        # the directory remains as a husk of things past
        super(BaseImageSeries, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        raise NotImplemented()

    def get_addimages_url(self):
        raise NotImplemented()

    def get_update_url(self):
        raise NotImplemented()

    def meta(self):
        return self._meta

    class Meta:
        abstract = True
        ordering = ['category', 'order', '-created']


class BaseImage(models.Model):
    image = ImageField(upload_to='images')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

    IMGIN_KEY = 'base'
    IMGIN_CFG = imgin.settings.IMGIN_CONFIG[IMGIN_KEY]

    @property
    def filename(self):
        return os.path.basename(self.image.name)

    @property
    def filename_without_extension(self):
        return os.path.splitext(self.filename)[0]

    @property
    def format(self):
        return os.path.splitext(self.filename)[1].lower()

    def get_url(self, size):
        has_http = False
        path, filename = os.path.split(self.image.url)
        if path[0:7].lower() == 'http://':
            has_http = True
            path = path[6:]

        filename, ext = os.path.splitext(filename)
        filename = '%s.%s' % (
            filename,
            self.IMGIN_CFG['size_map'][size]['format'].lower()
        )
        # skip up a dir from o/ subdir
        path = os.path.normpath(os.path.join(path, os.path.pardir))
        if has_http:
            path = 'http:/%s' % path

        return os.path.join(path, size, filename.lower())

    @property
    def url_l(self):
        has_http = False
        path, filename = os.path.split(self.image.url)
        if self.height != 600:
            return self.get_url('l')

        if path[0:7].lower() == 'http://':
            has_http = True
            path = path[6:]

        # skip up a dir from o/ subdir
        path = os.path.normpath(os.path.join(path, os.path.pardir))
        if has_http:
            path = 'http:/%s' % path
        return os.path.join(path, 'l', filename.lower())

    @property
    def url_m(self):
        return self.get_url('m')

    @property
    def url_s(self):
        return self.get_url('s')

    @property
    def url_t(self):
        return self.get_url('t')

    @property
    def is_portrait(self):
        return True if self.height > self.width else False

    @property
    def orientation(self):
        return 'portrait' if self.is_portrait else 'landscape'

    def delete_thumbs(self):
        """
        Deletes image's associated thumbnails
        """
        size_map = self.IMGIN_CFG['size_map']

        for sizedir, data in size_map.items():
            try:
                filename = os.path.join(
                    self.get_uploaddir(),
                    sizedir,
                    self.filename)
                filename_png = os.path.join(
                    self.get_uploaddir(),
                    sizedir,
                    '%s.%s' % (self.filename_without_extension, 'png')
                )
            except AttributeError:
                break
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(filename_png):
                os.remove(filename_png)

    def _calculate_wouldbe_size(self, geometry):
        x_image, y_image = map(float, (self.width, self.height))
        factors = (geometry[0] / x_image, geometry[1] / y_image)
        factor = min(factors)
        if factor:
            wouldbe_width = toint(x_image * factor)
            wouldbe_height = toint(y_image * factor)
            return (wouldbe_width, wouldbe_height)

    def _get_size_string(self, size_map):
        if self.is_portrait and 'min_width' in size_map:
            geometry = parse_geometry(
                size_map['portrait'],
                float(self.width) / self.height
            )
            (wouldbe_width, wouldbe_height) = \
                self._calculate_wouldbe_size(geometry)

            if int(size_map['min_width']) > wouldbe_width:
                # construct new size_map
                return size_map['min_width']
            else:
                return size_map[self.orientation]
        elif not self.is_portrait and 'min_height' in size_map:
            geometry = parse_geometry(
                size_map['landscape'],
                float(self.width) / self.height
            )
            (_, wouldbe_height) = \
                self._calculate_wouldbe_size(geometry)

            if int(size_map['min_height']) > wouldbe_height:
                # construct new size_map
                return size_map['min_height']
            else:
                return size_map[self.orientation]
        else:
            return size_map[self.orientation]

    def create_thumbs(self, *args, **kwargs):
        '''
        creates thumbnails from IMGIN's size_map
        '''
        size_map = self.IMGIN_CFG['size_map']

        for idx, data in size_map.items():
            size_string = self._get_size_string(size_map[idx])

            if self.height == 600 and idx == 'l':
                ext = self.format
                imgdir = os.path.join(
                    self.get_uploaddir(),
                    size_map[idx]['dir'])

                _mkdirs(imgdir)
                destination = os.path.abspath(
                    os.path.join(
                        imgdir, '%s%s' % (self.filename_without_extension,
                                          ext.lower())
                    )
                )
                try:
                    copyfile(self.image.path, destination)
                except OSError, e:
                    if e.errno != errno.EEXIST:
                        raise
                continue

            resized_src = get_thumbnail(
                self.image,
                size_string,
                crop=size_map[idx]['crop'],
                upscale=False,
                quality=size_map[idx]['quality'],
                format=size_map[idx]['format'],
            )
            ext = size_map[idx]['format']

            if ext[0] != '.':
                ext = '.%s' % ext

            imgdir = os.path.join(
                self.get_uploaddir(),
                size_map[idx]['dir'])

            _mkdirs(imgdir)

            resized_dest = os.path.abspath(
                os.path.join(
                    imgdir, '%s%s' % (
                        self.filename_without_extension,
                        ext.lower())
                )
            )

            f = open(resized_dest, 'w')
            f.write(resized_src.read())
            f.close()

    def get_dir_qualifier(self):
        '''
        this returns the specification of the models upload dir
        i.e. if it's part of a series, it could be /images/SERIES_ID/
        '''
        return ''

    def get_uploaddir(self):
        '''
        returns full directory to upload file into.
        override this if you need granular control
        '''
        return os.path.join(
            settings.MEDIA_ROOT,
            self.IMGIN_CFG['upload_dir'],
            str(self.get_dir_qualifier()),
        )

    def get_mediadir(self):
        '''
        returns relative directory for media upload dir, i.e. the
        directory we will use for returning thumbs in html etc.
        '''
        return os.path.join(
            self.IMGIN_CFG['upload_dir'],
            str(self.get_dir_qualifier()),
        )

    def populate(self, request, **kwargs):
        '''
        this gets called right before the image object is saved
        '''
        self.user_id = request.user.pk
        self.order = 0

    def handle_upload(self, request, *args, **kwargs):
        # read file info from stream
        uploaded = request.read
        filesize = int(uploaded.im_self.META["CONTENT_LENGTH"])
        uploaded_filename = uploaded.im_self.META["HTTP_X_FILE_NAME"]
        filename, fileextension = os.path.splitext(uploaded_filename)
        filename = "%s%s" % (uuid.uuid4(), fileextension.lower())

        # check first for allowed file extensions
        if not (self._get_ext_from_filename(filename) in
                self.IMGIN_CFG['allowed_exts']):
            return json.dumps({
                "error": "Filen har ikke et gyldig filformat."
            })

        # check file size
        if filesize > self.IMGIN_CFG['size_limit']:
            return json.dumps({
                "error": "Filen er for stor."
            })

        self.populate(request, **kwargs)

        uploaddir = os.path.join(self.get_uploaddir(), 'o')
        mediadir = os.path.join(self.get_mediadir(), 'o')

        _mkdirs(uploaddir)

        file = open(os.path.join(uploaddir, filename), "wb")
        file.write(request.read(filesize))
        file.close()

        self.image = self.image.field.attr_class(
            self, self.image.field,
            os.path.join(mediadir, filename))

        # get the WxH of original image
        image_obj = default.engine.get_image(self.image)
        (self.width, self.height) = \
            default.engine.get_image_size(image_obj)
        self.save()

        self.create_thumbs(**kwargs)

        return json.dumps(
            {
                'success': True,
                'url': self.image.url,
                'thumbnail_url': self.url_t,
                'id': self.id,
            }
        )

    def _get_ext_from_filename(self, filename):
        import os
        filename, extension = os.path.splitext(filename)
        return extension

    def delete(self, *args, **kwargs):
        self.delete_thumbs()

        try:
            sorl_delete(self.image)
        except AttributeError:
            pass
        super(BaseImage, self).delete(*args, **kwargs)

    @staticmethod
    def get_create_url(*args, **kwargs):
        raise NotImplemented()

    @staticmethod
    def get_delete_url(*args, **kwargs):
        raise NotImplemented()

    @staticmethod
    def get_upload_url(*args, **kwargs):
        raise NotImplemented()

    @staticmethod
    def get_list_url(*args, **kwargs):
        raise NotImplemented()

    def meta(self):
        return self._meta

    class Meta:
        ordering = ['order']
        abstract = True
