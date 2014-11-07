IMGIN
=====

**NOTE: This is tailored for the twined project structure,
it probably won't work too well without customization on other
project bootstraps.**

Installation:
-------------

    pip install -e git://github.com/twined/imgin.git#egg=imgin-dev


Usage:
------

Config:


    IMGIN_OPTIMIZE_CONFIG = {
        'png': '/usr/bin/optipng {filename}',
        'gif': '/usr/bin/optipng {filename}',
        'jpeg': '/usr/local/bin/jpegoptim {filename}'
    }

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

Base models:

  - class BaseFrontpageImage(models.Model):
  - class BaseImageCategory(models.Model):
  - class BaseImageSeries(models.Model):
  - class BaseImage(models.Model):


**BaseImage views:**

    class BaseImageCreateView(BaseTemplateView):
        model = BaseImage
        template_name = ''


    class AJAXBaseImageHandleUploadView(BaseView):
        model = BaseImage


    class BaseImageListView(ListView):
        model = BaseImage
        context_object_name = 'images'
        template_name = ''


    class AJAXBaseImageDeleteView(BaseView):
        model = BaseImage


    class AJAXBaseImageListView(BaseView):
        model = BaseImage


    class AJAXBaseImageSortView(BaseView):
        model_to_sort = BaseImage

**Management commands**

`optimize_images` - searches through media/images and optimizes all jpg
and png images.

*Install jpegoptim:*


    wget http://www.kokkonen.net/tjko/src/jpegoptim-1.4.1.tar.gz
    tar xvf jpegoptim-1.4.1.tar.gz
    cd jpegoptim-1.4.1
    ./configure
    make
    make strip
    sudo make install

*Install optipng:*


    wget http://downloads.sourceforge.net/project/optipng/OptiPNG/optipng-0.7.5/optipng-0.7.5.tar.gz
    tar xvf optipng-0.7.5.tar.gz
    cd optipng-0.7.5
    ./configure
    make
    sudo make install
