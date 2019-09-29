from django import template

register = template.Library()

@register.filter(name='addcss')
def addcss(field, css):
   return field.as_widget(attrs={"class":css})

@register.filter(name='_len')
def _len(elt):
    return len(elt)

@register.filter(name='get_obj')
def get_obj(a, b):
    return a[b]