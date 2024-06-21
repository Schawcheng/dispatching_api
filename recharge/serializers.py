from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from recharge.models import RechargeModel
from agent.models import AgentModel


class RechargeSerializer(serializers.ModelSerializer):
    agent = SerializerMethodField()

    def get_agent(self, obj):
        agent = AgentModel.objects.get(pk=obj.agent_id)
        return agent.phone

    class Meta:
        model = RechargeModel
        fields = '__all__'
