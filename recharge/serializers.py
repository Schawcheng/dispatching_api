from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from recharge.models import RechargeModel
from agent.models import AgentModel
from system_config.models import SystemConfigModel


class RechargeSerializer(serializers.ModelSerializer):
    agent = SerializerMethodField()
    receipt_address = SerializerMethodField()

    def get_agent(self, obj):
        agent = AgentModel.objects.filter(pk=obj.agent_id).first()

        if agent is None:
            return '该用户已被删除'
        return agent.phone

    def get_receipt_address(self, obj):
        record = SystemConfigModel.objects.get(title='receipt_address')

        return record.value

    class Meta:
        model = RechargeModel
        fields = '__all__'
