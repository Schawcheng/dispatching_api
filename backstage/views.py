from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from backstage.models import BackstageUserModel
from agent.models import AgentModel
from agent.serializers import AgentSerializer

import tools


class Login(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        captcha_code = request.data.get('captcha_code')

        # TODO: 图像验证码校验

        user = BackstageUserModel.objects.filter(username=username, password=tools.md5(password)).first()
        if not user:
            return Response(tools.api_response(404, '用户不存在或密码错误'))

        token = tools.generate_jwt(user.id, user.username, settings.SECRET_KEY)

        return Response(tools.api_response(200, '登录成功', {'token': token}))


class Agents(APIView):
    def get(self, request):
        records = AgentModel.objects.filter()

        total = records.count()

        for item in records:
            print(item)

        serializer = AgentSerializer(records, many=True)

        return Response(tools.api_response(200, 'OK', data=serializer.data, total=total))
