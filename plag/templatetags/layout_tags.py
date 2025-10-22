from django import template
from ..template_utils import get_layout_template

register = template.Library()

@register.filter
def get_user_layout(user):
    """Template filter to get appropriate layout for user"""
    return get_layout_template(user)