# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Managers for the Imgin application
# (c) Twined/Univers 2009-2013. All rights reserved.
# ----------------------------------------------------------------------

from random import randint
from django.db import models
from django.db.models import Count


class BaseFrontpageImageManager(models.Manager):
    def random(self):
        """
        Returns a random (Base)FrontpageImage object.
        """
        count = self.aggregate(count=Count('id'))['count']
        if not count:
            return
        random_index = randint(0, count - 1)
        return self.all()[random_index]
