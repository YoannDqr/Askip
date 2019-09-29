from django import template

from decimal import Decimal

register = template.Library()

@register.filter(name='mul')
def mul(d, f):
    exponent = Decimal('10') ** (-1)
    nb = '%E' % Decimal.from_float(f * 1.8).quantize(exponent)
    return nb.split('E')[0].rstrip('0').rstrip('.') + 'e' + nb.split('E')[1]

@register.filter(name='format_nb')
def format_nb(nb):
    return nb.quantize(Decimal('10') ** (-2))