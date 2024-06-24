from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from card.models import CardModel
from agent.models import AgentModel
from customer.models import CustomerModel


class CardSerializer(serializers.ModelSerializer):
    agent = SerializerMethodField()
    customer = SerializerMethodField()

    def get_agent(self, obj):
        agent = AgentModel.objects.get(pk=obj.agent_id)

        return agent.phone

    def get_customer(self, obj):
        if obj.customer_id is None:
            return '暂无'
        customer = CustomerModel.objects.get(pk=obj.customer_id)
        return customer.phone

    class Meta:
        model = CardModel
        fields = '__all__'
