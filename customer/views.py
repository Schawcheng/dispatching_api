from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response

from customer.CustomTokenAuthentication import JwtTokenAuthentication

from customer.models import CustomerModel

from card.models import CardModel
from card.serializers import CardSerializer
from agent.models import AgentModel

import tools


class RegisterView(APIView):
    def post(self, request):
        try:
            phone = request.data.get('phone')
            password = request.data.get('password')

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

            data = {
                'phone': me.phone,
                'points': me.points
            }

            return Response(tools.api_response(200, 'ok', data=data))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '获取用户信息失败'))


class RecycleView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            me = request.user
            status = int(request.GET.get('status'))

            records = CardModel.objects.filter(customer_id=me.pk)

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

            if key is None:
                return Response(tools.api_response(404, '卡密不能为空'))

            record_card = CardModel.objects.get(key=key)

            if record_card.status >= 2:
                return Response(tools.api_response(401, '此卡密已被使用，请更换卡密后再试'))

            record_customer = CustomerModel.objects.get(pk=me.pk)

            record_card.status = 2
            record_card.customer_id = record_customer.pk
            record_card.save(update_fields=['status', 'customer_id'])

            return Response(tools.api_response(200, '申请兑换成功, 请及时联系客服进行核销'))
        except CardModel.DoesNotExist:
            return Response(tools.api_response(404, '请填写有效的卡密'))
        except CustomerModel.DoesNotExist:
            return Response(tools.api_response(404, '请先登录'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '回收失败'))
