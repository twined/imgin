import logging
import errno
import subprocess
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import shutil
import json
import os
from PIL import Image
from tqdm import tqdm
from django.db.models.loading import get_model
from subprocess import check_output


from imgin.settings import IMGIN_OPTIMIZE_CONFIG

logger = logging.getLogger('imgin.optimize_images')


class Command(BaseCommand):
    help = 'Runs through all of the models images, optimizing pngs'
    args = '<app_name> <model_name>'

    def handle(self, *args, **options):
        if len(args) < 2:
            self.stdout.write(
                "<app_name> and <model_name> arguments are required")
            return
        app_name = args[0]
        model_name = args[1]
        model = get_model(app_name, model_name)

        images_count = model.objects.count()
        images = model.objects.all()
        self.stdout.write(
            "Optimizing PNGs.")
        self.stdout.write(
            "Progress (%s images to process)" % images_count)
        count = 0
        for image in images:
            # optimize pngs
            self._optimize(image)
            count += 1
            self.stdout.write(
                "\r%s/%s" % (count, images_count), ending="")

        self.stdout.write(
            "")
        self.stdout.write(
            "Finished processing!")

    def _optimize(self, image):
        #if image.pk == 129:
        #    import ipdb; ipdb.set_trace()
        try:
            optimize_command_src = IMGIN_OPTIMIZE_CONFIG['png']
            if not optimize_command_src:
                return
        except (TypeError, KeyError, NotImplementedError):
            return

        # get the imgin config for the model
        sizemap = image.IMGIN_CFG['size_map']

        for idx, data in sizemap.items():
            #import ipdb; ipdb.set_trace()
            self.stdout.write(
                "IDX %s" % idx)
            self.stdout.write(
                "DATA %s" % data)
            size_dir = sizemap[idx]['dir']
            format = data['format']
            if format == 'jpeg':
                # we only do pngs
                return
            if format == 'original':
                # check what the original image's format is
                if not image.get_format() == 'png':
                    return

            filename = os.path.join(
                image.get_uploaddir(),
                size_dir,
                image.filename_without_extension
            ) + '.png'

            if not os.path.exists(filename):
                self.stdout.write(
                    "File %s doesn't exist" % filename)
                continue

            new_filename = os.path.join(
                image.get_uploaddir(),
                size_dir,
                image.filename_without_extension
            ) + '-optimized' + '.png'

            original_size = os.path.getsize(filename)

            optimize_command = optimize_command_src.format(
                filename=filename,
                new_filename=new_filename
            )

            self.stdout.write(optimize_command)
            returncode = subprocess.call(optimize_command, stderr=subprocess.STDOUT, shell=True)

            if returncode == 15:
                self.stdout.write('%s already optimized.' % new_filename)

        image.optimized = True
        image.save()
