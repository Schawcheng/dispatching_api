import os.path
import traceback

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from agent.CustomTokenAuthentication import JwtTokenAuthentication

from agent.models import AgentModel
from agent.serializers import AgentSerializer

from recharge.models import RechargeModel
from recharge.serializers import RechargeSerializer

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
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        me = request.user
        records = AgentModel.objects.filter(parent_id=me.pk)
        total = records.count()
        serializer = AgentSerializer(records, many=True)
        return Response(tools.api_response(200, 'ok', data=serializer.data, total=total))


class RechargesView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        recharge_records = RechargeModel.objects.filter()
        total = recharge_records.count()
        serializer = RechargeSerializer(recharge_records, many=True)

        return Response(tools.api_response(200, 'ok', data=serializer.data, total=total))

    def post(self, request):
        try:
            points = request.data.get('points')
            me = request.user

            recharge_no = tools.generate_unique_order_number()

            recharge_record = RechargeModel.objects.filter(recharge_no=recharge_no).first()

            if recharge_record is not None:
                return Response(tools.api_response(500, '系统正忙，请稍后再试'))

            recharge_ = RechargeModel(
                recharge_no=recharge_no,
                points=points,
                agent_id=me.pk
            )
            recharge_.save()

            return Response(tools.api_response(200, '充值订单创建成功，请联系客服进行充值打款并上传充值截图'))
        except Exception as e:
            traceback.print_exc(e)
            return Response(tools.api_response(500, '充值失败,请稍后再试'))


class RechargeDetailView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request, recharge_no):
        import config.common
        try:
            cert = request.data.get('cert', None)

            if not cert:
                return Response(tools.api_response(401, '未读取到文件'))

            cert_suffix = os.path.splitext(cert.name)[-1]

            if cert_suffix not in ['.jpg', '.jpeg', '.png']:
                return Response(tools.api_response(401, '仅支持 jpg, jpeg, png 格式的文件'))

            cert_name = tools.generate_unique_string(prefix='cert-')

            cert_fullname = cert_name + cert_suffix
            cert_path = os.path.join(config.common.RECHARGE_CERT_ROOT_DIR, cert_fullname)

            with open(cert_path, 'wb+') as f:
                if cert.multiple_chunks():
                    for chunk in cert.chunks():
                        f.write(chunk)
                else:
                    f.write(cert.read())

            cert_url = os.path.join(config.common.RECHARGE_CERT_ROOT_URL, cert_fullname)

            recharge_record = RechargeModel.objects.get(recharge_no=recharge_no)
            recharge_record.recharge_cert = cert_url
            recharge_record.save(update_fields=['recharge_cert'])
            return Response(tools.api_response(200, '上传成功'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '上传失败'))
