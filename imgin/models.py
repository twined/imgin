# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Base Models for the Imgin application
# (c) Twined/Univers 2009-2013. All rights reserved.
# ----------------------------------------------------------------------

import json
import os
import uuid

from math import log
from PIL import Image

from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.template.defaultfilters import slugify

import imgin.settings

from .managers import BaseFrontpageImageManager
from .tasks import optimize_png
from .utils import _mkdirs
from .utils import get_image_size
from .utils import get_thumbnail
from .utils import parse_geometry
from .utils import toint


def imgin_upload_handler(self, filename):
    upload_path = 'images'
    try:
        filename, extension = os.path.splitext(filename)
        f = "%s%s" % (
            os.path.join(upload_path,
                         slugify(filename.lower())), extension.lower())
    except:
        raise ImproperlyConfigured('You need to set upload_path')
    return f


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
    slug = models.CharField('URL', max_length=255)
    credits = models.CharField('Krediteringer', blank=True, max_length=255)
    #  user = models.ForeignKey(User)
    user = models.ForeignKey(
        User, related_name="%(app_label)s_%(class)s_set")
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

    def recreate_thumbs(self):
        if hasattr(self, 'related_images'):
            for im in self.related_images.all():
                im.recreate_thumbs()

    def meta(self):
        return self._meta

    class Meta:
        abstract = True
        ordering = ['category', 'order', '-created']


class BaseImage(models.Model):
    IMGIN_KEY = 'base'
    IMGIN_CFG = imgin.settings.IMGIN_CONFIG[IMGIN_KEY]

    image = models.ImageField(upload_to=imgin_upload_handler)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    optimized = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(BaseImage, self).__init__(*args, **kwargs)
        for name in self.IMGIN_CFG['size_map'].iterkeys():
            if name is None:
                continue
            fget = lambda self, name = name: self.get_url(name)
            setattr(BaseImage, 'url_%s' % name, property(fget=fget))

    @property
    def ratio(self):
        return float(self.height)/float(self.width)*100

    @property
    def filename(self):
        return os.path.basename(self.image.name)

    @property
    def filename_without_extension(self):
        return os.path.splitext(self.filename)[0]

    def get_format(self):
        patterns = (
            (['.png'], 'png'),
            (['.jpg', '.jpe', '.jpeg'], 'jpeg'),
            (['.gif'], 'gif'),
            (['.tif', '.tiff'], 'tiff'),
            (['.bmp', '.dib'], 'bmp'),
            (['.dcx'], 'dcx'),
            (['.eps', 'ps'], 'eps'),
            (['.im'], 'im'),
            (['.pcd'], 'pcd'),
            (['.pcx'], 'pcx'),
            (['.pdf'], 'pdf'),
            (['.pbm', '.pgm', '.ppm'], 'ppm'),
            (['.psd'], 'psd'),
            (['.xbm'], 'xbm'),
            (['.xpm'], 'xpm')
        )
        if '.' not in self.filename:
            return None
        ext = os.path.splitext(self.filename)[1].lower()
        for pattern in patterns:
            if ext in pattern[0]:
                return pattern[1]
        return None

    def responsive_url(self, matched_media_queries):
        size_map = self.IMGIN_CFG['size_map']
        for size_map_key, size_map_data in size_map.items():
            media_queries = size_map_data.get('media_queries')
            if not media_queries:
                continue
            for media_query in media_queries:
                if len(set(media_query).intersection(
                        matched_media_queries)) == len(media_query):
                    return self.get_url(size_map_key)

        return self.get_url()

    def get_url(self, size=None):
        if not size:
            try:
                size = self.IMGIN_CFG['default_map']
            except KeyError:
                raise ImproperlyConfigured(
                    "No `default_map` key set in IMGIN_CFG for %s" %
                    self.__class__.__name__
                )
        format = self.IMGIN_CFG['size_map'][size]['format']

        size = self.IMGIN_CFG['size_map'][size]['dir']

        if format == 'original':
            format = self.get_format()

        has_http = False
        path, filename = os.path.split(self.image.url)
        if path[0:7].lower() == 'http://':
            has_http = True
            path = path[6:]

        only_filename, ext = os.path.splitext(filename)
        filename = '%s.%s' % (
            only_filename,
            format.lower()
        )
        filename_optimized = '%s-optimized.%s' % (
            only_filename,
            format.lower()
        )
        # skip up a dir from o/ directory
        path = os.path.normpath(os.path.join(path, os.path.pardir))
        if has_http:
            path = 'http:/%s' % path

        if self.optimized and self.get_format() is 'png':
            if os.path.exists(os.path.join(settings.MEDIA_ROOT,
                                           self.get_mediadir(),
                                           size, filename_optimized)):
                return os.path.join(path, size, filename_optimized.lower())

        return os.path.join(path, size, filename.lower())

    @property
    def is_portrait(self):
        return True if self.height > self.width else False

    @property
    def orientation(self):
        return 'portrait' if self.is_portrait else 'landscape'

    @property
    def entropy(self):
        with open(str(self.image.file), 'rb') as f:
            im = Image.open(f)
            histogram = im.histogram()

        log2 = lambda x: log(x)/log(2)

        total = len(histogram)
        counts = {}
        for item in histogram:
            counts.setdefault(item, 0)
            counts[item] += 1

        ent = 0
        for i in counts:
            p = float(counts[i])/total
            ent -= p*log2(p)
        return -ent*log2(1/ent)

    def recreate_thumbs(self):
        self.delete_thumbs()
        self.create_thumbs()

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
                filename_optimized_png = os.path.join(
                    self.get_uploaddir(),
                    sizedir,
                    '%s-optimized.%s' % (self.filename_without_extension, 'png')
                )
                filename_jpeg = os.path.join(
                    self.get_uploaddir(),
                    sizedir,
                    '%s.%s' % (self.filename_without_extension, 'jpeg')
                )
            except AttributeError:
                break
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(filename_png):
                os.remove(filename_png)
            if os.path.exists(filename_optimized_png):
                os.remove(filename_optimized_png)
            if os.path.exists(filename_jpeg):
                os.remove(filename_jpeg)

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
            self.create_thumb(idx)

        if self.get_format() == 'png' and 'optimize_png' in self.IMGIN_CFG:
            if self.IMGIN_CFG['optimize_png'] is True:
                optimize_png.delay(self)

    def create_thumb(self, idx):
        size_map = self.IMGIN_CFG['size_map']
        size_string = self._get_size_string(size_map[idx])
        format = size_map[idx]['format']
        if format == 'original':
            format = self.get_format()

        resized_src = get_thumbnail(
            self.image,
            size_string,
            crop=size_map[idx]['crop'],
            upscale=True if idx is 't' else False,
            quality=size_map[idx]['quality'],
            format=format,
        )

        ext = format

        if ext[0] != '.':
            ext = '.%s' % ext

        imgdir = os.path.join(
            self.get_uploaddir(),
            size_map[idx]['dir'])

        _mkdirs(imgdir)

        resized_image_destination_path = os.path.abspath(
            os.path.join(
                imgdir, '%s%s' % (
                    self.filename_without_extension,
                    ext.lower()
                )
            )
        )

        resized_src.save(
            resized_image_destination_path,
            quality=size_map[idx]['quality'] or 90,
            optimize=True)

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
        image_obj = Image.open(self.image)
        (self.width, self.height) = \
            get_image_size(image_obj)
        self.save()

        self.create_thumbs(**kwargs)

        return json.dumps(
            {
                'success': True,
                'url': self.image.url,
                'thumbnail_url': self.url_t,
                'large_url': self.url_l,
                'id': self.id,
            }
        )

    def handle_froala_upload(self, request, *args, **kwargs):
        # read file info from stream
        if 'file' not in request.FILES:
            return json.dumps({
                "error": "Ingen gjenkjennelig fil lastet opp."
            })

        file = request.FILES['file']
        filesize = file.size
        fileextension = file.name.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), fileextension)

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

        fd = open(os.path.join(uploaddir, filename), 'wb')
        for chunk in file.chunks():
            fd.write(chunk)
        fd.close()

        self.image = self.image.field.attr_class(
            self, self.image.field,
            os.path.join(mediadir, filename))

        # get the WxH of original image
        image_obj = Image.open(self.image)
        (self.width, self.height) = \
            get_image_size(image_obj)
        self.save()

        self.create_thumbs(**kwargs)

        return json.dumps({'link': self.url_l})

    def handle_villain_upload(self, request, *args, **kwargs):
        # read file info from stream
        if 'file' not in request.FILES:
            return json.dumps({
                "error": "Ingen gjenkjennelig fil lastet opp."
            })

        file = request.FILES['file']
        filesize = file.size
        fileextension = file.name.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), fileextension)

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

        fd = open(os.path.join(uploaddir, filename), 'wb')
        for chunk in file.chunks():
            fd.write(chunk)
        fd.close()

        self.image = self.image.field.attr_class(
            self, self.image.field,
            os.path.join(mediadir, filename))

        # get the WxH of original image
        image_obj = Image.open(self.image)
        (self.width, self.height) = \
            get_image_size(image_obj)
        self.save()

        self.create_thumbs(**kwargs)

        return True

    def _get_ext_from_filename(self, filename):
        import os
        filename, extension = os.path.splitext(filename)
        return extension

    def delete(self, *args, **kwargs):
        # deletes the image and any connected thumbnails
        self.delete_thumbs()
        try:
            self.image.storage.delete(self.image)
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
