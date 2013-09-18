import os.path
from django.conf import settings
from django import template
from django.template import Library

register = Library()

emotions_root = '/static/images/data/emotions/'
emotions_dir = os.path.abspath(os.path.dirname(__file__) + '/..' + emotions_root) + '/'

@register.filter
def replace_to_emotion(string, ext='.png'):
    """ 
    replace the [] in {string} to emotions.

    usage: {{ "[smile] I'm a string."|replace_to_emotion }}
    results: <img src="/static/images/data/emotions/smile.png" /> I'm a string
    """
    new_string = []
    for s in string.split(' '):
        if not s.startswith('[') and not s.endswith(']'):
            new_string.append(s)
            continue
        tmp_s = s[1:-1]
        if not os.path.exists(emotions_dir + tmp_s + ext):
            new_string.append(s)
            continue
        s = '<img src="%s" alt="%s" title="%s" />' % (
            os.path.join(settings.PROJECT_URL_PREFIX, emotions_root, tmp_s + ext),
            tmp_s,
            tmp_s,
        )
        new_string.append(s)
    return ' '.join(new_string)
