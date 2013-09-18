from django.http import HttpResponse, Http404
from django.core import serializers
from django.utils import simplejson
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

import random, time, models

chat_with_user_session_key = 'chat_with_user'
chat_receive_timeout = 20

def receive_messages(request):
    """
    Get stored messages with long polling technology.
    """
    if not request.user.is_authenticated() or not request.session.get(chat_with_user_session_key):
        raise Http404
    chat_with_user = request.session[chat_with_user_session_key]
    cache_key = '%s_to_%s' % (chat_with_user.username, request.user.username)
    
    # FIXME: Following code has been disabled for workaround broken pipe
    #        with long polling in uwsgi.
    #messages = []
    #step = 0
    #while not messages and step < chat_receive_timeout:
    #    messages = cache.get(cache_key)
    #    if messages:
    #        break;
    #    step += 1
    #    time.sleep(1)

    messages = cache.get(cache_key)
    if not messages:
        raise Http404
    cache.set(cache_key, []);
    return HttpResponse(simplejson.dumps({
        'rc': 200,
        'messages': messages
    }))

@csrf_exempt
def post_message(request):
    """
    Use cache to fake a poll for chat
    """
    if not request.user.is_authenticated() or not request.session.get(chat_with_user_session_key):
        raise Http404
    if not request.REQUEST.get('message'):
        raise Http404
    chat_with_user = request.session[chat_with_user_session_key]
    cache_key = '%s_to_%s' % (request.user.username, chat_with_user.username)
    message = {
        'message': request.REQUEST['message'],
        'post_at': datetime.now().strftime("%H:%M:%S"),
    }
    
    messages = cache.get(cache_key)
    if not messages:
        messages = []
    messages.append(message)
    cache.set(cache_key, messages)
    return HttpResponse(simplejson.dumps({'rc': 200}))

def update_emotion(request):
    """
    1. Update user emotion;
    2. Find a random people with same emotion and response.
    """
    emotion_id = request.REQUEST.get('emotion_id')
    if not request.user.is_authenticated() or not emotion_id:
        raise Http404

    # Clean up chat with user
    if request.session.get(chat_with_user_session_key):
        del request.session[chat_with_user_session_key]
    
    # Update user emotion profile
    profile, create = models.UserProfile.objects.get_or_create(
        user = request.user
    )
    profile.emotion_id = emotion_id
    profile.save()
    
    # Find peoples with same emotion
    profiles = models.UserProfile.objects.filter(emotion_id = emotion_id)
    profiles = profiles.exclude(user = request.user)
    if len(profiles) == 0:
        return HttpResponse(simplejson.dumps({
            'rc': 404,
        }))

    chat_with_user = profiles[random.randint(0, len(profiles) - 1)].user
    request.session[chat_with_user_session_key] = chat_with_user
    return HttpResponse(simplejson.dumps({
        'rc': 200,
        'chat_with_user' : {
            'id': chat_with_user.pk,
            'username': chat_with_user.username
        }
    }))
