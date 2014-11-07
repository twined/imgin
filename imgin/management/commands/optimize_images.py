'''
jpegoptim:
wget http://www.kokkonen.net/tjko/src/jpegoptim-1.4.1.tar.gz
tar xvf jpegoptim-1.4.1.tar.gz
cd jpegoptim-1.4.1
./configure
make
make strip
sudo make install

optipng:
wget http://downloads.sourceforge.net/project/optipng/OptiPNG/optipng-0.7.5/optipng-0.7.5.tar.gz
tar xvf optipng-0.7.5.tar.gz
cd optipng-0.7.5
./configure
make
sudo make install

'''

import os
import subprocess
import logging
from imghdr import what as determinetype
from subprocess import check_output

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import get_storage_class
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile

from imgin.settings import IMGIN_OPTIMIZE_CONFIG

logger = logging.getLogger('imgin.optimize_images')


class Command(BaseCommand):
    help = 'Optimizes png and jpeg images in media directory'

    def handle(self, *args, **options):
        self.stdout.write(
            "Searching for large images in media directory")
        src_dir = os.path.join(settings.MEDIA_ROOT, 'images')
        print src_dir
        for root, dirs, files in os.walk(src_dir):
            for fn in files:
                path = os.path.join(root, fn)
                size = os.stat(path).st_size  # in bytes
                if size > 50000:
                    self._optimize(path)

    def _optimize(self, filename):
        storage_class = get_storage_class()
        storage = storage_class()
        orgfile = storage.open(filename)

        try:
            optimize_command = IMGIN_OPTIMIZE_CONFIG[
                determinetype(orgfile)]
            if not optimize_command:
                return
        except (TypeError, KeyError, NotImplementedError):
            return

        print('- Optimizing %s' % filename)
        size_org = orgfile.size
        with NamedTemporaryFile() as temp_file:
            orgfile.seek(0)
            temp_file.write(orgfile.read())
            temp_file.flush()
            optimize_command = optimize_command.format(filename=temp_file.name)
            output = check_output(
                optimize_command, stderr=subprocess.STDOUT, shell=True)
            if output:
                logger.warn(
                    '{0} returned {1}'.format(optimize_command, output))
            else:
                logger.info('{0} returned nothing'.format(optimize_command))
            with open(temp_file.name, 'rb') as f:
                orgfile.file = ContentFile(f.read())
                storage.delete(orgfile.name)
                storage.save(orgfile.name, orgfile)
                size_new = orgfile.size
                size_diff = size_org - size_new
                logger.info('saved {0} bytes'.format(size_diff))
                print('>> Saved %s bytes' % size_diff)
