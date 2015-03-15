from django import template

from ..forms import get_category_choices

register = template.Library()


@register.assignment_tag
def get_categories():
    return get_category_choices()
