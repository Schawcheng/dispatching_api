import decimal
import os
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response

from customer.CustomTokenAuthentication import JwtTokenAuthentication

from customer.models import CustomerModel
from customer.serializers import CustomerSerializer

from card.models import CardModel
from card.serializers import CardSerializer
from agent.models import AgentModel

from withdraw.models import WithdrawModel
from withdraw.serializers import WithdrawSerializer

from bank.models import BankModel
from bank.serializers import BankSerializer

import tools

import config.common
import utils.upload_file


class RegisterView(APIView):
    def post(self, request):
        try:
            phone = request.data.get('phone')
            password = request.data.get('password')

            record_customer = CustomerModel.objects.filter(phone=phone).first()

            if record_customer is not None:
                return Response(tools.api_response(401, '此账号已被注册'))

            record = CustomerModel(phone=phone, password=password)
            record.save()

            return Response(tools.api_response(200, '注册成功'))

        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '注册失败'))


class LoginView(APIView):
    def post(self, request):
        try:
            phone = request.data.get('phone')
            password = request.data.get('password')

            record = CustomerModel.objects.get(phone=phone, password=tools.md5(password))

            token = tools.generate_jwt(record.pk, record.phone, settings.SECRET_KEY)

            data = {
                'token': token,
            }

            return Response(tools.api_response(200, '登录成功', data=data))

        except CustomerModel.DoesNotExist:
            return Response(tools.api_response(404, '账号不存在或密码错误'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '登录失败'))


class CustomerInfoView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user

            serializer = CustomerSerializer(me)
            return Response(tools.api_response(200, 'ok', data=serializer.data))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '获取用户信息失败'))


class RecycleView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user
            status = int(request.GET.get('status'))

            records = CardModel.objects.filter(customer_id=me.pk).order_by('-id')

            if status == 3:
                records = records.filter(status=status)

            if status == 4:
                records = records.filter(status=status)

            total = records.count()
            serializer = CardSerializer(records, many=True)

            return Response(tools.api_response(200, 'ok', data=serializer.data, total=total))

        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '获取订单列表失败'))

    def post(self, request):
        try:
            me = request.user
            key = request.data.get('key', None)
            password = request.data.get('password', None)
            face_value = request.data.get('face_value', None)

            if face_value is None:
                return Response(tools.api_response(401, '请选择有效的面值'))

            if key is None:
                return Response(tools.api_response(401, '卡号不能为空'))

            if password is None:
                return Response(tools.api_response(401, '卡密不能为空'))

            record_card = CardModel.objects.get(key=key, password=password)

            if record_card.status >= 2:
                return Response(tools.api_response(401, '此卡密已被使用，请更换卡密后再试'))

            face_value = decimal.Decimal(face_value)

            if face_value != record_card.points:
                return Response(tools.api_response(401, '选择的面值与您输入的卡号面值不一致'))

            record_customer = CustomerModel.objects.get(pk=me.pk)

            record_card.status = 2
            record_card.card_no = tools.generate_unique_order_number()
            record_card.customer_id = record_customer.pk
            record_card.save(update_fields=['status', 'card_no', 'customer_id'])

            return Response(tools.api_response(200, '申请兑换成功, 请及时联系客服进行核销'))
        except CardModel.DoesNotExist:
            return Response(tools.api_response(404, '卡号无效或卡密错误'))
        except CustomerModel.DoesNotExist:
            return Response(tools.api_response(404, '请先登录'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '回收失败'))


class PaymentDetailView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def post(self, request):
        try:
            me = request.user
            payment_type = request.data.get('payment_type')
            content = request.data.get('file', None)

            if content is None:
                return Response(tools.api_response(401, '请选择有效的内容上传'))

            qrcode_suffix = os.path.splitext(content.name)[-1]

            if qrcode_suffix not in ['.jpg', '.jpeg', '.png']:
                return Response(tools.api_response(401, '仅支持 jpg, jpeg, png 格式的文件'))

            if payment_type == 'alipay':
                qrcode_path, qrcode_filename = utils.upload_file.handle_upload_file_save_path(
                    config.common.CUSTOMER_QRCODE_ROOT_DIR,
                    qrcode_suffix, prefix='alipay-')

                utils.upload_file.save_django_upload_file(content, qrcode_path)
                qrcode_url = utils.upload_file.generate_file_url(config.common.CUSTOMER_QRCODE_ROOT_URL,
                                                                 qrcode_filename)

                me.alipay_qrcode = qrcode_url
                me.save(update_fields=['alipay_qrcode'])
                return Response(tools.api_response(200, '上传支付宝收款码成功'))

            if payment_type == 'wechat':
                qrcode_path, qrcode_filename = utils.upload_file.handle_upload_file_save_path(
                    config.common.CUSTOMER_QRCODE_ROOT_DIR, qrcode_suffix, prefix='wechat-')

                utils.upload_file.save_django_upload_file(content, qrcode_path)
                qrcode_url = utils.upload_file.generate_file_url(config.common.CUSTOMER_QRCODE_ROOT_URL,
                                                                 qrcode_filename)

                me.wechat_qrcode = qrcode_url
                me.save(update_fields=['wechat_qrcode'])
                return Response(tools.api_response(200, '上传微信收款码成功'))

            return Response(tools.api_response(401, '不支持此收款方式'))

        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '上传失败'))


class BanksView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user
            record_bank = BankModel.objects.filter(user_id=me.pk, is_agent=0).first()

            if record_bank is None:
                return Response(tools.api_response(200, 'ok', data=None))
            serializer = BankSerializer(record_bank)
            return Response(tools.api_response(200, 'ok', data=serializer.data))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '获取银行卡信息失败'))

    def post(self, request):
        try:
            me = request.user
            username = request.data.get('username', None)
            bank_name = request.data.get('bank_name', None)
            bank_account = request.data.get('bank_account')
            register_bank = request.data.get('register_bank', None)

            if not all([username, bank_name, bank_account, register_bank]):
                return Response(tools.api_response(401, '银行卡信息不完整'))

            record_bank = BankModel.objects.filter(user_id=me.pk, is_agent=0).first()

            if record_bank is not None:
                record_bank.username = username
                record_bank.bank_name = bank_name
                record_bank.bank_account = bank_account
                record_bank.register_bank = register_bank
                record_bank.save(update_fields=[
                    'username',
                    'bank_name',
                    'bank_account',
                    'register_bank'
                ])
                return Response(tools.api_response(200, '修改成功'))

            bank_obj = BankModel(
                username=username,
                bank_name=bank_name,
                bank_account=bank_account,
                register_bank=register_bank,
                user_id=me.pk,
                is_agent=0
            )
            bank_obj.save()

            return Response(tools.api_response(200, '绑定成功'))

        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '绑定失败'))


class WithdrawView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user
            records = WithdrawModel.objects.filter(is_agent=0, user_id=me.pk).order_by('-id')
            status = int(request.GET.get('status'))

            if status > -1:
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

            if me.points <= 0:
                return Response(tools.api_response(401, '余额不足以提现'))

            if points > me.points:
                return Response(tools.api_response(401, '余额不足'))

            record_withdraw = WithdrawModel(
                withdraw_no=tools.generate_unique_order_number(),
                points=points,
                user_id=me.pk,
                is_agent=0,
                payment_type=payment_type,
                status=0
            )

            record_withdraw.save()

            me.points -= points
            me.save(update_fields=['points'])

            return Response(tools.api_response(200, '提现申请成功'))

        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '提现申请失败'))
