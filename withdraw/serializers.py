from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from withdraw.models import WithdrawModel

from customer.models import CustomerModel
from agent.models import AgentModel


class WithdrawSerializer(serializers.ModelSerializer):
    user = SerializerMethodField()
    payment = SerializerMethodField()

    def get_user(self, obj):
        if obj.is_agent == 0:
            user = CustomerModel.objects.get(pk=obj.user_id)
        else:
            user = AgentModel.objects.get(pk=obj.user_id)

        return user.phone

    def get_payment(self, obj):
        user = None
        if obj.is_agent == 0:
            user = CustomerModel.objects.get(pk=obj.user_id)
        else:
            user = AgentModel.objects.get(pk=obj.user_id)

        if obj.payment_type == 1:
            return user.alipay_qrcode

        if obj.payment_type == 2:
            return user.wechat_qrcode

        if obj.payment_type == 3:
            return user.bank

        if obj.payment_type == 4:
            return user.usdt_address

        return '暂不支持的付款方式'

    class Meta:
        model = WithdrawModel
        fields = '__all__'
