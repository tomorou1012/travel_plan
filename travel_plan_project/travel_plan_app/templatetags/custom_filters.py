from django import template
import logging

register = template.Library()
logger = logging.getLogger(__name__)

@register.filter
def get_item(dictionary, key):
    logger.debug("f[TEMPLATE] get_item called with key='{key} in dict='{dictionary}")
    return dictionary.get(key)