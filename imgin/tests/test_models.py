import os

from django.test import TestCase
from django.core.files import File
from django.conf import settings
from django.contrib.auth.models import User
from django.test.client import RequestFactory

from sorl.thumbnail import default
import factory

from ..models import BaseImage


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    first_name = 'John'
    last_name = 'Doe'
    email = 'john@doe.com'
    #admin = False


class PfImage(BaseImage):
    pass
    #class Meta:
    #    app_label = 'imgin'


class ImginModelTests(TestCase):
    def setUp(self):
        self.dir = os.path.split(__file__)[0]
        settings.MEDIA_ROOT = os.path.join(
            self.dir, "media")
        self.object = PfImage()
        self.object.image = File(open(
            os.path.join(settings.MEDIA_ROOT, "images/portfolio/o/logo.png")))
        self.object.image = self.object.image.field.attr_class(
            self.object, self.object.image.field,
            'images/portfolio/o/logo.png'
        )

        image_obj = default.engine.get_image(self.object.image)
        (self.object.width, self.object.height) = \
            default.engine.get_image_size(image_obj)

        self.object.user = UserFactory()
        self.object.order = 0

        self.object.IMGIN_CFG = {
            'allowed_exts': [".jpg", ".png", ".jpeg",
                             ".JPG", ".PNG", ".JPEG"],
            'belongs_to': 'ImageSeries',
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
        }

        #self.object.save()

    def test_handle_upload(self):
        pass
        # create a request
        #reqfactory = RequestFactory()
        #request = reqfactory.factory.get(reverse('/'))
        #self.object.handle_upload(reqfactory)

    def test_url_generation(self):
        self.assertEqual(self.object.url_t,
                         '/media/images/portfolio/o/../t/logo.png')
        self.assertEqual(self.object.url_s,
                         '/media/images/portfolio/o/../s/logo.png')
        self.assertEqual(self.object.url_m,
                         '/media/images/portfolio/o/../m/logo.png')
        self.assertEqual(self.object.url_l,
                         '/media/images/portfolio/o/../l/logo.png')
        self.object.height = 600
        self.assertEqual(self.object.url_l,
                         '/media/images/portfolio/o/../l/logo.png')

    def test_filename(self):
        self.assertEqual(self.object.filename, 'logo.png')

    def test_filename_without_extension(self):
        self.assertEqual(self.object.filename_without_extension, 'logo')

    def test_format(self):
        self.assertEqual(self.object.format, '.png')

    def test_is_portrait(self):
        self.assertFalse(self.object.is_portrait)

    def test_orientation(self):
        self.assertEqual(self.object.orientation, 'landscape')

    def test_create_thumbs(self):
        self.object.create_thumbs()
        self.assertTrue(os.path.exists('%s%s' % (self.dir, self.object.url_s)))
        self.assertTrue(os.path.exists('%s%s' % (self.dir, self.object.url_m)))
        self.assertTrue(os.path.exists('%s%s' % (self.dir, self.object.url_l)))
        self.assertTrue(os.path.exists('%s%s' % (self.dir, self.object.url_t)))

    def test_delete_thumbs(self):
        pass
