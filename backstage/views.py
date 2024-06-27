import decimal
import traceback

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from backstage.models import BackstageUserModel
from backstage.CustomTokenAuthentication import JwtTokenAuthentication

from agent.models import AgentModel
from agent.serializers import AgentSerializer

from system_config.models import SystemConfigModel
from system_config.serializers import SystemConfigSerializer

from recharge.models import RechargeModel
from recharge.serializers import RechargeSerializer

from card.models import CardModel
from card.serializers import CardSerializer

from customer.models import CustomerModel

from withdraw.models import WithdrawModel
from withdraw.serializers import WithdrawSerializer

import tools


class LoginView(APIView):
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


class AgentsView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        records = AgentModel.objects.filter()
        total = records.count()
        serializer = AgentSerializer(records, many=True)

        return Response(tools.api_response(200, 'OK', data=serializer.data, total=total))


class SystemConfigsView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            records = SystemConfigModel.objects.all()
            serializer = SystemConfigSerializer(records, many=True)

            return Response(tools.api_response(200, 'ok', data=serializer.data))
        except Exception:
            return Response(tools.api_response(500, '系统配置获取失败'))


class SystemConfigDetailView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request, config_id):
        try:
            value = request.data.get('value')
            record = SystemConfigModel.objects.get(pk=config_id)
            record.value = value
            record.save(update_fields=['value'])
            return Response(tools.api_response(200, '修改成功'))
        except Exception:
            return Response(tools.api_response(500, '系统配置修改失败'))


class RechargesView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            records = RechargeModel.objects.all()
            total = records.count()
            serializer = RechargeSerializer(records, many=True)
            return Response(tools.api_response(200, 'ok', data=serializer.data, total=total))
        except Exception:
            return Response(tools.api_response(500, '获取充值记录失败'))


class RechargeDetailView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request, recharge_id):
        try:
            status = request.data.get('status')

            record_recharge = RechargeModel.objects.get(pk=recharge_id)
            record_recharge.status = status
            record_recharge.save()

            if status == 1:
                record_agent = AgentModel.objects.get(pk=record_recharge.agent_id)
                record_agent.points += record_recharge.points
                record_agent.save(update_fields=['points'])

            return Response(tools.api_response(200, '操作成功'))
        except Exception:
            return Response(tools.api_response(500, '操作失败'))


class CardsView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            records = CardModel.objects.all()
            total = records.count()

            serializer = CardSerializer(records, many=True)

            return Response(tools.api_response(200, 'ok', data=serializer.data, total=total))
        except Exception:
            return Response(tools.api_response(500, '获取卡密失败'))

    def post(self, request):
        try:
            agent_id = request.data.get('agent_id')
            points = request.data.get('points')
            quantity = request.data.get('quantity')

            record_agent = AgentModel.objects.get(pk=agent_id)

            if points * quantity > record_agent.points:
                return Response(tools.api_response(401, '积分不足以对应数量的卡密扣取'))

            record_agent.points -= points

            record_agent.save(update_fields=['points'])

            for i in range(quantity):
                key = tools.generate_unique_key()
                card_obj = CardModel(
                    key=key,
                    points=points,
                    agent_id=agent_id,
                )
                card_obj.save()

            return Response(tools.api_response(200, '发卡成功'))

        except Exception as e:
            traceback.print_exc(e)
            return Response(tools.api_response(500, '发卡失败'))


class AgentStatisticsView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            records = AgentModel.objects.all()
            total = records.count()
            return Response(tools.api_response(200, 'ok', total=total))
        except Exception as e:
            print(e)


class RechargesStatisticsView(APIView):
    def get(self, request):
        try:
            records = RechargeModel.objects.all()
            total = records.count()
            return Response(tools.api_response(200, 'ok', total=total))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '获取充值总量失败'))


class RecycleView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request):
        try:
            key = request.data.get('key')

            record_card = CardModel.objects.get(key=key)
            record_customer = CustomerModel.objects.get(pk=record_card.customer_id)

            current_agent = AgentModel.objects.get(pk=record_card.agent_id)

            lv1_agent = AgentModel.objects.filter(pk=current_agent.parent_id).first()

            lv2_agent = None

            lv3_agent = None

            if lv1_agent is not None:
                lv2_agent = AgentModel.objects.filter(pk=lv1_agent.parent_id).first()

            if lv2_agent is not None:
                lv3_agent = AgentModel.objects.filter(pk=lv2_agent.parent_id).first()

            lv1_rate = decimal.Decimal(SystemConfigModel.objects.get(title='lv1').value)
            lv2_rate = decimal.Decimal(SystemConfigModel.objects.get(title='lv2').value)
            lv3_rate = decimal.Decimal(SystemConfigModel.objects.get(title='lv3').value)

            if lv1_agent is not None:
                lv1_agent.points += record_card.points * lv1_rate
                lv1_agent.save(update_fields=['points'])

            if lv2_agent is not None:
                lv2_agent.points += record_card.points * lv2_rate
                lv2_agent.save(update_fields=['points'])

            if lv3_agent is not None:
                lv3_agent.points += record_card.points * lv3_rate
                lv3_agent.save(update_fields=['points'])

            record_card.status = 3
            record_card.save(update_fields=['status'])

            record_customer.points += record_card.points
            record_customer.save(update_fields=['points'])

            return Response(tools.api_response(200, '核销成功'))

        except CardModel.DoesNotExist:
            return Response(tools.api_response(404, '卡密无效'))
        except CustomerModel.DoesNotExist:
            return Response(tools.api_response(404, '找不到用户'))
        except Exception as e:
            traceback.print_exc(e)
            return Response(tools.api_response(500, '核销失败'))


class CardsStatisticsView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            records = CardModel.objects.all()
            total = records.count()

            recycled_count = records.filter(status=3).count()
            un_recycled_count = records.filter().exclude(status=3).count()
            data = {
                'total': total,
                'recycled_count': recycled_count,
                'un_recycled_count': un_recycled_count
            }
            return Response(tools.api_response(200, 'ok', data=data))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '获取卡密总数失败'))


class WithdrawView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            records = WithdrawModel.objects.all()
            total = records.count()
            serializer = WithdrawSerializer(records, many=True)

            return Response(tools.api_response(200, 'ok', data=serializer.data, total=total))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '获取提现记录失败'))


class WithdrawDetailView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request, withdraw_no):
        try:
            status = int(request.data.get('status'))
            record = WithdrawModel.objects.get(withdraw_no=withdraw_no)

            record.status = status
            record.save(update_fields=['status'])

            return Response(tools.api_response(200, '操作成功'))

        except WithdrawModel.DoesNotExist:
            return Response(tools.api_response(404, '提现订单不存在'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '操作失败'))
