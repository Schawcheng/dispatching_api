import datetime
import decimal
import os.path
import traceback

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

import config.common
from agent.CustomTokenAuthentication import JwtTokenAuthentication

from agent.models import AgentModel
from agent.serializers import AgentSerializer

from recharge.models import RechargeModel
from recharge.serializers import RechargeSerializer

from card.models import CardModel
from card.serializers import CardSerializer

from withdraw.models import WithdrawModel
from withdraw.serializers import WithdrawSerializer

import tools

import utils.upload_file


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
        me = request.user
        recharge_records = RechargeModel.objects.filter(agent_id=me.pk)
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


class CardsView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user
            records = CardModel.objects.filter(agent_id=me.pk)
            total = records.count()
            serializer = CardSerializer(records, many=True)
            return Response(tools.api_response(200, 'ok', data=serializer.data, total=total))
        except Exception:
            return Response(tools.api_response(500, '获取卡密列表失败'))


class PaymentTypesView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user
            record_agent = AgentModel.objects.get(pk=me.pk)

            ret = {
                'usdt': record_agent.usdt_address,
                'alipay': record_agent.alipay_qrcode,
                'wechat': record_agent.wechat_qrcode,
                'bank': record_agent.bank
            }
            return Response(tools.api_response(200, 'ok', data=ret))
        except Exception:
            return Response(tools.api_response(500, '获取收款方式失败'))


class PaymentTypeDetailView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request):
        try:
            me = request.user
            payment_type = request.data.get('payment_type')
            content = request.data.get('content', None)

            if content is None:
                return Response(tools.api_response(401, '请选择有效的内容上传'))

            record_agent = AgentModel.objects.get(pk=me.pk)

            if payment_type == 'usdt':
                record_agent.usdt_address = content
                record_agent.save(update_fields=['usdt_address'])
                return Response(tools.api_response(200, 'usdt地址修改成功'))

            if payment_type == 'bank':
                record_agent.bank = content
                record_agent.save(update_fields=['bank'])
                return Response(tools.api_response(200, '银行卡账号修改成功'))

            qrcode_suffix = os.path.splitext(content.name)[-1]

            if qrcode_suffix not in ['.jpg', '.jpeg', '.png']:
                return Response(tools.api_response(401, '仅支持 jpg, jpeg, png 格式的文件'))

            if payment_type == 'alipay':
                qrcode_path, qrcode_filename = utils.upload_file.handle_upload_file_save_path(
                    config.common.QRCODE_ROOT_DIR,
                    qrcode_suffix, prefix='alipay-')

                utils.upload_file.save_django_upload_file(content, qrcode_path)
                qrcode_url = utils.upload_file.generate_file_url(config.common.QRCODE_ROOT_URL, qrcode_filename)

                record_agent.alipay_qrcode = qrcode_url
                record_agent.save(update_fields=['alipay_qrcode'])
                return Response(tools.api_response(200, '上传支付宝收款码成功'))

            if payment_type == 'wechat':
                qrcode_path, qrcode_filename = utils.upload_file.handle_upload_file_save_path(
                    config.common.QRCODE_ROOT_DIR, qrcode_suffix, prefix='wechat-')

                utils.upload_file.save_django_upload_file(content, qrcode_path)
                qrcode_url = utils.upload_file.generate_file_url(config.common.QRCODE_ROOT_URL, qrcode_filename)

                record_agent.wechat_qrcode = qrcode_url
                record_agent.save(update_fields=['wechat_qrcode'])
                return Response(tools.api_response(200, '上传微信收款码成功'))

            return Response(tools.api_response(404, '暂时不支持的收款方式'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '上传失败'))


class MyPointsView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user
            record_agent = AgentModel.objects.get(pk=me.pk)
            points = record_agent.points

            return Response(tools.api_response(200, 'ok', data={'points': points}))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '获取我的积分失败'))


class SubordinatesStatisticsView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user
            records_agent = AgentModel.objects.filter(parent_id=me.pk)
            total = records_agent.count()
            return Response(tools.api_response(200, 'ok', total=total))
        except Exception:
            return Response(tools.api_response(500, '获取团队人数失败'))


class MyCardsStatistic(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user
            record_cards = CardModel.objects.filter(agent_id=me.pk)
            total = record_cards.count()
            return Response(tools.api_response(200, 'ok', total=total))
        except Exception:
            return Response(tools.api_response(500, '获取卡密总数失败'))


class WithdrawsView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user
            status = int(request.GET.get('status'))
            records = WithdrawModel.objects.filter(is_agent=1, user_id=me.pk)

            if status > 0:
                records = records.filter(status=status)

            total = records.count()

            serializer = WithdrawSerializer(records, many=True)

            return Response(tools.api_response(200, 'ok', data=serializer.data, total=total))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '获取提现记录失败'))

    def post(self, request):
        try:
            me = request.user
            points = decimal.Decimal(request.data.get('points'))
            payment_type = int(request.data.get('payment_type'))

            if points < 0:
                return Response(tools.api_response(401, '请输入有效的提现金额'))

            if points > me.points:
                return Response(tools.api_response(401, '提现金额不能大于您的余额'))

            record_withdraw = WithdrawModel(
                withdraw_no=tools.generate_unique_order_number(),
                points=points,
                user_id=me.pk,
                is_agent=1,
                payment_type=payment_type,
                status=0
            )
            record_withdraw.save()
            me.points -= points
            me.save(update_fields=['points'])
            return Response(tools.api_response(200, '提现申请成功，等待客服审核'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '提现申请失败'))


class MyInfoView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user
            serializer = AgentSerializer(me)
            return Response(tools.api_response(200, 'ok', data=serializer.data))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '获取个人信息失败'))

    def put(self, request):
        try:
            me = request.user
            password = request.data.get('password', None)

            if password is None:
                return Response(tools.api_response(401, '密码不能为空'))

            record = AgentModel.objects.get(pk=me.pk)
            record.password = password
            record.save(update_fields=['password'])
            return Response(tools.api_response(200, '修改成功'))
        except AgentModel.DoesNotExist:
            return Response(tools.api_response(404, '账号不存在'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '修改失败'))


class TotalTransactionsStatisticsView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user
            records_agent = AgentModel.objects.filter(parent_id=me.pk)

            transaction_total = 0
            today_total = 0
            for item in records_agent:
                records_card = CardModel.objects.filter(agent_id=item.pk, status=3)
                transaction_total += records_card.count()

                today = datetime.datetime.now().date()
                records_card = records_card.filter(create_time__gte=today)
                today_total += records_card.count()

            my_total = CardModel.objects.filter(agent_id=me.pk, status=3).count()

            data = {
                'transaction_total': transaction_total,
                'today_total': today_total,
                'my_total': my_total
            }

            return Response(tools.api_response(200, 'ok', data=data))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '获取团队总交易量失败'))
