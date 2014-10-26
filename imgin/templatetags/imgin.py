from django import template

register = template.Library()


@register.filter
def ratio(image):
    if not image:
        return 0
    return float(image.height)/float(image.width)*100

'''
from images.models import ImageSeries, ImageCategory

register = template.Library()


@register.inclusion_tag(
    'images/templatetags/images/get_portfolio_category_links.html',
    takes_context=True)
def get_portfolio_category_links(context, category='', active_category=''):
    image_series = ImageSeries.objects.select_related().filter(category__slug=category)

    return {
        'image_series': image_series,
        'category': category,
        'active_category': active_category,
    }


@register.inclusion_tag(
    'images/templatetags/images/display_menu.html',
    takes_context=True)
def display_menu(context, active_category='', request=''):
    image_categories = ImageCategory.objects.all()

    return {
        'image_categories': image_categories,
        'active_category': active_category,
        'request': request,
    }
'''
