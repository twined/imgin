import os
import subprocess

from django_rq import job

from .settings import IMGIN_OPTIMIZE_CONFIG


@job
def optimize_png(image):
    try:
        optimize_command_src = IMGIN_OPTIMIZE_CONFIG['png']
        if not optimize_command_src:
            return
    except (TypeError, KeyError, NotImplementedError):
        return

    # get the imgin config for the model
    sizemap = image.IMGIN_CFG['size_map']

    for idx, data in sizemap.items():
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
            continue

        new_filename = os.path.join(
            image.get_uploaddir(),
            size_dir,
            image.filename_without_extension
        ) + '-optimized' + '.png'

        optimize_command = optimize_command_src.format(
            filename=filename,
            new_filename=new_filename
        )

        returncode = subprocess.call(
            optimize_command,
            stderr=subprocess.STDOUT, shell=True)

        # if returncode == 15:
        #    self.stdout.write('%s already optimized.' % new_filename)

    image.optimized = True
    image.save()
