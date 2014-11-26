import os

from django.test import TestCase
from django.test import SimpleTestCase
from django.core.files import File
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
# from django.test.client import RequestFactory

from mock_django.models import ModelMock
from PIL import Image
from django_rq import get_worker

from imgin import utils
from imgin.helpers import ImginError

from .models import PfImage


class ImginModelTests(SimpleTestCase):
    def setUp(self):
        self.dir = settings.MEDIA_ROOT
        self.object_jpeg = PfImage()
        self.object_jpeg.image = File(open(
            os.path.join(settings.MEDIA_ROOT, 'images', 'o', "test.jpg")))
        self.object_jpeg.image = self.object_jpeg.image.field.attr_class(
            self.object_jpeg, self.object_jpeg.image.field,
            'images/o/test.jpg'
        )

        image_obj = utils.get_image(self.object_jpeg.image)
        (self.object_jpeg.width, self.object_jpeg.height) = \
            utils.get_image_size(image_obj)

        self.object_jpeg.user = ModelMock(User)
        self.object_jpeg.order = 0

        self.object_png = PfImage()
        self.object_png.image = File(open(
            os.path.join(settings.MEDIA_ROOT, 'images', 'o', "test2.png")))
        self.object_png.image = self.object_png.image.field.attr_class(
            self.object_png, self.object_png.image.field,
            'images/o/test2.png'
        )

        image_obj = utils.get_image(self.object_png.image)
        (self.object_png.width, self.object_png.height) = \
            utils.get_image_size(image_obj)

        self.object_png.user = ModelMock(User)
        self.object_png.order = 0

    def tearDown(self):
        self.object_jpeg.delete_thumbs()
        self.object_png.delete_thumbs()

    def test_handle_upload(self):
        pass
        # create a request
        '''
        reqfactory = RequestFactory()
        request = reqfactory.get(reverse('/'))
        self.object_jpeg.handle_upload(request)
        '''

    def test_model_properties(self):
        self.assertTrue(hasattr(self.object_jpeg, 'url_thumb'))
        self.assertTrue(hasattr(self.object_jpeg, 'url_small'))
        self.assertTrue(hasattr(self.object_jpeg, 'url_medium'))
        self.assertTrue(hasattr(self.object_jpeg, 'url_large'))

        self.assertTrue(hasattr(self.object_png, 'url_thumb'))
        self.assertTrue(hasattr(self.object_png, 'url_small'))
        self.assertTrue(hasattr(self.object_png, 'url_medium'))
        self.assertTrue(hasattr(self.object_png, 'url_large'))

    def test_url_generation(self):
        self.assertEqual(self.object_jpeg.url_thumb,
                         'images/thumb/test.jpeg')
        self.assertEqual(self.object_jpeg.url_small,
                         'images/small/test.jpeg')
        self.assertEqual(self.object_jpeg.url_medium,
                         'images/medium/test.jpeg')
        self.assertEqual(self.object_jpeg.url_large,
                         'images/large/test.jpeg')

        self.assertEqual(self.object_png.url_thumb,
                         'images/thumb/test2.png')
        self.assertEqual(self.object_png.url_small,
                         'images/small/test2.png')
        self.assertEqual(self.object_png.url_medium,
                         'images/medium/test2.png')
        self.assertEqual(self.object_png.url_large,
                         'images/large/test2.png')

    def test_get_url(self):
        self.assertEqual(self.object_jpeg.get_url(), 'images/medium/test.jpeg')
        self.assertEqual(self.object_png.get_url(), 'images/medium/test2.png')

    def test_filename(self):
        self.assertEqual(self.object_jpeg.filename, 'test.jpg')
        self.assertEqual(self.object_png.filename, 'test2.png')

    def test_filename_without_extension(self):
        self.assertEqual(self.object_jpeg.filename_without_extension, 'test')
        self.assertEqual(self.object_png.filename_without_extension, 'test2')

    def test_format(self):
        self.assertEqual(self.object_jpeg.get_format(), 'jpeg')
        self.assertEqual(self.object_png.get_format(), 'png')

    def test_is_portrait(self):
        self.assertTrue(self.object_jpeg.is_portrait)
        self.assertFalse(self.object_png.is_portrait)

    def test_orientation(self):
        self.assertEqual(self.object_jpeg.orientation, 'portrait')
        self.assertEqual(self.object_png.orientation, 'landscape')

    def test_create_thumbs(self):
        self.object_jpeg.create_thumbs()
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.url_small)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.url_medium)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.url_large)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.url_thumb)))

        self.object_png.create_thumbs()
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_png.url_small)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_png.url_medium)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_png.url_large)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_png.url_thumb)))

    def test_delete_thumbs(self):
        self.object_jpeg.create_thumbs()
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.url_small)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.url_medium)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.url_large)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.url_thumb)))
        self.object_jpeg.delete_thumbs()
        self.assertFalse(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.url_small)))
        self.assertFalse(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.url_medium)))
        self.assertFalse(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.url_large)))
        self.assertFalse(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.url_thumb)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_jpeg.image.url)))

        self.object_png.create_thumbs()
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_png.url_small)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_png.url_medium)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_png.url_large)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_png.url_thumb)))
        self.object_png.delete_thumbs()
        self.assertFalse(
            os.path.exists(os.path.join(self.dir, self.object_png.url_small)))
        self.assertFalse(
            os.path.exists(os.path.join(self.dir, self.object_png.url_medium)))
        self.assertFalse(
            os.path.exists(os.path.join(self.dir, self.object_png.url_large)))
        self.assertFalse(
            os.path.exists(os.path.join(self.dir, self.object_png.url_thumb)))
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_png.image.url)))

    def test_ratio(self):
        self.assertEqual(self.object_png.ratio, 39.599609375)

    def test_responsive_url(self):
        self.assertEqual(
            self.object_png.responsive_url(['mobile']),
            'images/small/test2.png')
        self.assertEqual(
            self.object_png.responsive_url(['retina']),
            'images/large/test2.png')
        self.assertEqual(
            self.object_png.responsive_url([]),
            'images/medium/test2.png')


class ImginUtilsTests(SimpleTestCase):
    def setUp(self):
        self.dir = settings.MEDIA_ROOT
        self.object_jpeg = PfImage()
        self.object_jpeg.image = File(open(
            os.path.join(settings.MEDIA_ROOT, 'images', 'o', "test.jpg")))
        self.object_jpeg.image = self.object_jpeg.image.field.attr_class(
            self.object_jpeg, self.object_jpeg.image.field,
            'images/o/test.jpg'
        )
        self.pil_jpeg = Image.open(self.object_jpeg.image.path)

        image_obj = utils.get_image(self.object_jpeg.image)
        (self.object_jpeg.width, self.object_jpeg.height) = \
            utils.get_image_size(image_obj)

        self.object_jpeg.user = ModelMock(User)
        self.object_jpeg.order = 0

        self.object_png = PfImage()
        self.object_png.image = File(open(
            os.path.join(settings.MEDIA_ROOT, 'images', 'o', 'test2.png')))
        self.object_png.image = self.object_png.image.field.attr_class(
            self.object_png, self.object_png.image.field,
            'images/o/test2.png'
        )

        image_obj = utils.get_image(self.object_png.image)
        (self.object_png.width, self.object_png.height) = \
            utils.get_image_size(image_obj)

        self.object_png.user = ModelMock(User)
        self.object_png.order = 0

        self.pil_png = Image.open(self.object_png.image.path)

    def tearDown(self):
        self.object_jpeg.delete_thumbs()
        self.object_png.delete_thumbs()

    def test_merge_settings(self):
        a = {
            'movies': {
                'actors': 10,
                'studios': 1,
            },
            'test': 100,
            'test2': 50
        }

        b = {
            'test2': 100,
            'movies': {
                'studios': 5,
                'execs': 1
            }
        }

        c = utils.merge_settings(a, b)

        self.assertTrue(c['test'] is 100)
        self.assertTrue(c['test2'] is 100)
        self.assertTrue(c['movies']['execs'] is 1)
        self.assertTrue(c['movies']['studios'] is 5)
        self.assertTrue(c['movies']['actors'] is 10)

    def test_is_transparent(self):
        self.assertFalse(utils.is_transparent(self.pil_jpeg))
        self.assertFalse(utils.is_transparent(self.object_jpeg.image))

        self.assertFalse(utils.is_transparent(self.pil_png))
        self.assertFalse(utils.is_transparent(self.object_png.image))

    def test_is_progressive(self):
        self.assertFalse(utils.is_progressive(self.pil_jpeg))
        self.assertFalse(utils.is_progressive(self.object_jpeg.image))

        self.assertFalse(utils.is_progressive(self.pil_png))
        self.assertFalse(utils.is_progressive(self.object_png.image))

    def test_get_thumbnail(self):
        self.assertFalse(utils.get_thumbnail(None, None))
        invalid_file = File(os.path.join(settings.MEDIA_ROOT,
                                         'images', 'o', 'invalid_file.jpg'))
        self.assertFalse(utils.get_thumbnail(invalid_file, None))

    def test_parse_geometry(self):
        self.assertRaises(ImginError, utils.parse_geometry, '1xx55x1')
        self.assertEqual(utils.parse_geometry('50x50'), (50, 50))


class ImginTasksTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        from django.test.client import Client

        # store the password to login later
        password = 'mypassword'

        self.user = User.objects.create_superuser('myuser', 'myemail@test.com',
                                                  password)
        self.c = Client()

        # You'll need to log him in before you can send requests
        # through the client
        self.c.login(username=self.user.username, password=password)

        self.dir = settings.MEDIA_ROOT
        self.object_jpeg = PfImage()
        self.object_jpeg.image = File(open(
            os.path.join(settings.MEDIA_ROOT, 'images', 'o', "test.jpg")))
        self.object_jpeg.image = self.object_jpeg.image.field.attr_class(
            self.object_jpeg, self.object_jpeg.image.field,
            'images/o/test.jpg'
        )
        self.pil_jpeg = Image.open(self.object_jpeg.image.path)

        image_obj = utils.get_image(self.object_jpeg.image)
        (self.object_jpeg.width, self.object_jpeg.height) = \
            utils.get_image_size(image_obj)

        self.object_jpeg.user = self.user
        self.object_jpeg.order = 0

        self.object_jpeg.save()

        self.object_png = PfImage()
        self.object_png.image = File(open(
            os.path.join(settings.MEDIA_ROOT, 'images', 'o', 'test2.png')))
        self.object_png.image = self.object_png.image.field.attr_class(
            self.object_png, self.object_png.image.field,
            'images/o/test2.png'
        )

        image_obj = utils.get_image(self.object_png.image)
        (self.object_png.width, self.object_png.height) = \
            utils.get_image_size(image_obj)

        self.object_png.user = self.user
        self.object_png.order = 0

        self.pil_png = Image.open(self.object_png.image.path)

        self.object_png.save()

    def tearDown(self):
        self.object_jpeg.delete_thumbs()
        self.object_png.delete_thumbs()

        self.user.delete()

    def test_optimize_png(self):
        from imgin.tasks import optimize_png
        # first we create the thumbs
        self.object_png.create_thumbs()

        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_png.url_large)))
        self.assertEqual(self.object_png.get_url(),
                         'images/medium/test2.png')
        self.assertFalse(self.object_png.optimized)

        optimize_png(self.object_png)

        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_png.url_large)))
        self.assertEqual(self.object_png.get_url(),
                         'images/medium/test2-optimized.png')
        self.assertTrue(self.object_png.optimized)
        self.assertTrue(
            os.path.exists(os.path.join(self.dir, self.object_png.url_large)))

        optimize_png(self.object_jpeg)


class ImginViewsTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        from django.test.client import Client

        # store the password to login later
        password = 'mypassword'

        self.user = User.objects.create_superuser('myuser', 'myemail@test.com',
                                                  password)
        self.c = Client()

        # You'll need to log him in before you can send requests
        # through the client
        self.c.login(username=self.user.username, password=password)

        self.dir = settings.MEDIA_ROOT
        self.object_jpeg = PfImage()
        self.object_jpeg.image = File(open(
            os.path.join(settings.MEDIA_ROOT, 'images', 'o', "test.jpg")))
        self.object_jpeg.image = self.object_jpeg.image.field.attr_class(
            self.object_jpeg, self.object_jpeg.image.field,
            'images/o/test.jpg'
        )
        self.pil_jpeg = Image.open(self.object_jpeg.image.path)

        image_obj = utils.get_image(self.object_jpeg.image)
        (self.object_jpeg.width, self.object_jpeg.height) = \
            utils.get_image_size(image_obj)

        self.object_jpeg.user = self.user
        self.object_jpeg.order = 0

        self.object_jpeg.save()

        self.object_png = PfImage()
        self.object_png.image = File(open(
            os.path.join(settings.MEDIA_ROOT, 'images', 'o', 'test2.png')))
        self.object_png.image = self.object_png.image.field.attr_class(
            self.object_png, self.object_png.image.field,
            'images/o/test2.png'
        )

        image_obj = utils.get_image(self.object_png.image)
        (self.object_png.width, self.object_png.height) = \
            utils.get_image_size(image_obj)

        self.object_png.user = self.user
        self.object_png.order = 0

        self.pil_png = Image.open(self.object_png.image.path)

        self.object_png.save()

    def tearDown(self):
        self.object_jpeg.delete_thumbs()
        self.object_png.delete_thumbs()

        self.user.delete()

    def test_image_create_view(self):
        response = self.c.get(reverse('image-create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['images']), 2)

    def test_image_list_view(self):
        response = self.c.get(reverse('image-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['images']), 2)
