"""
// Twined - Imgin
// template tag definitions for the Imgin app
// (c) Twined/Univers 2009-2014. All rights reserved.
"""

import logging
from django import template
from classytags.core import Tag, Options
from classytags.arguments import Argument, KeywordArgument
from thumbnailfield.fields import ThumbnailFieldFile

register = template.Library()

logger = logging.getLogger(__name__)


@register.filter
def ratio(image):
    if not image:
        return 0
    return float(image.height)/float(image.width)*100


class GetResponsiveImage(Tag):
    name = 'get_responsive_image'
    options = Options(
        Argument('image'),
        KeywordArgument('crop', required=False, resolve=False)
    )

    def render_tag(self, context, image, crop):
        device = context['device']
        return image.responsive_url(device.matched)


register.tag(GetResponsiveImage)


class GetResponsiveImageObject(Tag):
    name = 'get_responsive_image_object'
    options = Options(
        Argument('image'),
        'as',
        Argument('varname', resolve=False),
        KeywordArgument('crop', required=False, resolve=False)
    )

    def render_tag(self, context, image, varname, crop):
        if not image:
            return ''
        device = context['device']
        mq_use = ''
        if isinstance(image, ThumbnailFieldFile):
            logger.debug('&& render_tag - isinstance(ThumbnailFieldFile)')
            if not image.instance:
                logger.debug('&& render_tag - no image.instance)')
                return ''

            mq_map = image.instance.media_queries.get(image.field.name)
            logger.debug('&& mq_map =')
            logger.debug(mq_map)

            if not mq_map:
                logger.debug('&& render_tag - no mq_map')
                context[varname] = ''
                return ''

            if crop:
                # look for keys with crop- in them
                logger.debug('&& render_tag - crop')
                matches = {key: val for key, val in mq_map.items() if
                           key.startswith('crop')}
                logger.debug('&& matches = %s' % matches)
            else:
                # look for keys without crop- in them
                logger.debug('&& render_tag - no crop')
                matches = {key: val for key, val in mq_map.items() if
                           not key.startswith('crop')}
                logger.debug('&& matches = %s' % matches)

            for mq_key, media_queries in matches.items():
                if not media_queries:
                    logger.debug('&& not media_queries')
                    mq_use = mq_key
                    continue
                for media_query in media_queries:
                    logger.debug('&& media_query = %s' % media_query)
                    if len(set(media_query).intersection(device.matched)) == len(media_query):
                        logger.debug('&& render_tag - media_query - match found')
                        mq_use = mq_key

            if not mq_use:
                context[varname] = image
                return ''

            try:
                image_object = getattr(image, mq_use)
            except AttributeError:
                context[varname] = ''
                return ''

            if not image_object:
                context[varname] = ''
                return ''

            context[varname] = image_object
            return ''


register.tag(GetResponsiveImageObject)


class GetResponsiveUrl(Tag):
    name = 'get_responsive_url'
    options = Options(
        Argument('image'),
        'as',
        Argument('varname', required=False, resolve=False)
    )

    def render_tag(self, context, image, varname):
        device = context['device']
        output = image.responsive_url(device.matched)

        if varname:
            context[varname] = output
            return ''
        else:
            return output

register.tag(GetResponsiveUrl)
