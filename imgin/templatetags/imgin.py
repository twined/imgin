from django import template
from classytags.core import Tag, Options
from classytags.arguments import Argument, KeywordArgument
from classytags.helpers import AsTag
from thumbnailfield.fields import ThumbnailFieldFile

register = template.Library()


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
        '''
        return '<img src="%(url)s" title="%(title)s" alt="%(title)s" width="%(width)s" height="%(height)s" />' % {
            'url': image.responsive_url(device.matched),
            'title': image.title,
            'width': image.width,
            'height': image.height
        }
        '''


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
        device = context['device']
        mq_use = ''
        if isinstance(image, ThumbnailFieldFile):
            if not image.instance:
                return ''

            mq_map = image.instance.media_queries.get(image.field.name)

            if not mq_map:
                context[varname] = ''
                return ''

            if crop:
                # look for keys with crop- in them
                matches = {key: val for key, val in mq_map.items() if
                           key.startswith('crop')}
            else:
                # look for keys without crop- in them
                matches = {key: val for key, val in mq_map.items() if
                           not key.startswith('crop')}

            for mq_key, media_queries in matches.items():
                if not media_queries:
                    mq_use = mq_key
                    continue
                for media_query in media_queries:
                    if len(set(media_query).intersection(device.matched)) == len(media_query):
                        mq_use = mq_key

            image_object = getattr(image, mq_use)

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
