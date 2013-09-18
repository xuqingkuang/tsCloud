from django.contrib.auth.models import User
from tsCloud.ctauth.models import CTAuthMap

username_field = 'user_id'
token_field = 'surfing_token'

class CTUserTokenMiddleware(object):
    def process_request(self, request, mail_tail = '@189.cn'):
        username = request.REQUEST.get(username_field)
        token = request.REQUEST.get(token_field)

        if not username or not token:
            return

        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist, err:
            user = User.objects.create(
                username = username,
                email = username + mail_tail
            )
            user.set_password('abc123')
            user.save()

        try:
            user_token_map = CTAuthMap.objects.get(user = user)
            user_token_map.token = token
            user_token_map.save()
        except CTAuthMap.DoesNotExist, err:
            user_token_map = CTAuthMap.objects.create(
                user = user,
                token = token
            )

        request.user = user
