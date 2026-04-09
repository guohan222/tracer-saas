from django import template

register = template.Library()


@register.simple_tag
def use_storage(size):
    if size > 1024 * 1024 * 1024:  # GB
        return '{:.2f}GB'.format(size / (1024 * 1024 * 1024))
    elif size > 1024 * 1024:  # MB
        return '{:.2f}MB'.format(size / (1024 * 1024))
    elif size > 1024:  # KB
        return '{:.2f}KB'.format((size / 1024))
    else:
        return f'{size}B'
