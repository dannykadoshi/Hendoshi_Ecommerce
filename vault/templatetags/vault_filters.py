from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def cloudinary_transform(value, arg):
    """
    Transform Cloudinary URLs by inserting transformation parameters.
    Usage: {{ url|cloudinary_transform:"w_400,h_400,c_fill,f_auto,q_auto" }}
    """
    if '/upload/' in value:
        return value.replace('/upload/', f'/upload/{arg}/')
    return value
