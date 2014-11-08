import os

from django.test import TestCase
from django.test import SimpleTestCase
from django.core.files import File
from django.conf import settings
from django.contrib.auth.models import User
from django.test.client import RequestFactory


from mock_django.models import ModelMock


from imgin.utils import get_image
from imgin.utils import get_image_size

from .models import PfImage


class ImginModelTests(SimpleTestCase):
    def setUp(self):
        self.dir = settings.MEDIA_ROOT
        self.object = PfImage()
        self.object.image = File(open(
            os.path.join(settings.MEDIA_ROOT, 'images', 'o', "test.jpg")))
        self.object.image = self.object.image.field.attr_class(
            self.object, self.object.image.field,
            'images/o/test.jpg'
        )

        image_obj = get_image(self.object.image)
        (self.object.width, self.object.height) = \
            get_image_size(image_obj)

        self.object.user = ModelMock(User)
        self.object.order = 0

    def tearDown(self):
        self.object.delete_thumbs()

    '''
    def test_handle_upload(self):
        pass
        # create a request
        #reqfactory = RequestFactory()
        #request = reqfactory.factory.get(reverse('/'))
        #self.object.handle_upload(reqfactory)
    '''

    def test_model_properties(self):
        self.assertTrue(hasattr(self.object, 'url_thumb'))
        self.assertTrue(hasattr(self.object, 'url_small'))
        self.assertTrue(hasattr(self.object, 'url_medium'))
        self.assertTrue(hasattr(self.object, 'url_large'))

    def test_url_generation(self):
        self.assertEqual(self.object.url_thumb,
                         'images/thumb/test.jpg')
        self.assertEqual(self.object.url_small,
                         'images/small/test.jpg')
        self.assertEqual(self.object.url_medium,
                         'images/medium/test.jpg')
        self.assertEqual(self.object.url_large,
                         'images/large/test.jpg')

    def test_get_url(self):
        self.assertEqual(self.object.get_url(), 'images/medium/test.jpg')

    def test_filename(self):
        self.assertEqual(self.object.filename, 'test.jpg')

    def test_filename_without_extension(self):
        self.assertEqual(self.object.filename_without_extension, 'test')

    def test_format(self):
        self.assertEqual(self.object.format, '.jpg')

    def test_is_portrait(self):
        self.assertTrue(self.object.is_portrait)

    def test_orientation(self):
        self.assertEqual(self.object.orientation, 'portrait')

    def test_create_thumbs(self):
        self.object.create_thumbs()
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object.url_small)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object.url_medium)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object.url_large)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object.url_thumb)))

    def test_delete_thumbs(self):
        self.object.create_thumbs()
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object.url_small)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object.url_medium)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object.url_large)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object.url_thumb)))
        self.object.delete_thumbs()
        self.assertFalse(
            os.path.exists(os.path.join(self.dir, self.object.url_small)))
        self.assertFalse(
            os.path.exists(os.path.join(self.dir, self.object.url_medium)))
        self.assertFalse(
            os.path.exists(os.path.join(self.dir, self.object.url_large)))
        self.assertFalse(
            os.path.exists(os.path.join(self.dir, self.object.url_thumb)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object.image.url)))
