from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from agent.CustomTokenAuthentication import TokenAuthentication

from agent.models import AgentModel
from agent.serializers import AgentSerializer

import tools


class RegisterView(APIView):
    def post(self, request):
        phone = request.data.get('phone_number', None)
        password = request.data.get('password', None)
        invitation_code = request.data.get('invitation_code')

        record = AgentModel.objects.filter(phone=phone).first()

        if record is not None:
            return Response(tools.api_response(401, '此账号已被注册'))

        parent = AgentModel.objects.filter(invitation_code=invitation_code).first()

        if parent is None:
            return Response(tools.api_response(401, '无效的邀请码'))

        agt = AgentModel(
            phone=phone,
            password=password,
            parent_id=parent.id,
        )
        agt.save()

        self_invitation_code = tools.generate_unique_invitation_code(phone)
        agt.invitation_code = self_invitation_code
        agt.save(update_fields=['invitation_code'])

        return Response(tools.api_response(200, '注册成功，请及时在个人设置上传收款方式'))


class LoginView(APIView):
    def post(self, request):
        phone = request.data.get('phone', None)
        password = request.data.get('password', None)
        captcha_code = request.data.get('captcha_code', None)

        if not all([phone, password]):
            return Response(tools.api_response(401, '请输入合法的账号密码'))

        try:
            agt = AgentModel.objects.get(phone=phone, password=tools.md5(password))

            token = tools.generate_jwt(agt.pk, agt.phone, settings.SECRET_KEY)
            return Response(tools.api_response(200, '登录成功', {'token': token}))
        except AgentModel.DoesNotExist:
            return Response(tools.api_response(404, '账号不存在或密码错误'))


class SubordinatesView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        me = request.user
        records = AgentModel.objects.filter(parent_id=me.pk)
        total = records.count()
        serializer = AgentSerializer(records, many=True)
        return Response(tools.api_response(200, 'ok', data=serializer.data, total=total))


class RechargeView(APIView):
    def post(self, request):
        pass
