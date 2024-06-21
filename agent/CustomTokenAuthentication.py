from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from agent.models import AgentModel
from rest_framework.exceptions import AuthenticationFailed
import jwt
from jwt import ExpiredSignatureError


class JwtTokenAuthentication(BaseAuthentication):
    def authenticate(self, request, *args, **kwargs):
        auth_token: str = request.META.get('HTTP_AUTHORIZATION')

        if not auth_token:
            raise AuthenticationFailed('请先登录')
        try:
            # token = auth_token.split(' ')[1] # 如果token形式如 JWT header.payload.signature 形式才需要这个操作
            payload = jwt.decode(auth_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            user = AgentModel.objects.get(pk=user_id)
        except ExpiredSignatureError:
            raise AuthenticationFailed('登录已过期，请重新登录')
        except AgentModel.DoesNotExist:
            raise AgentModel.DoesNotExist('用户不存在')

        return user, auth_token
