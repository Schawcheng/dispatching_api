import datetime

from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from agent.models import AgentModel

from recharge.models import RechargeModel

from card.models import CardModel


class AgentSerializer(serializers.ModelSerializer):
    parent = SerializerMethodField()
    subordinates_count = SerializerMethodField()
    my_total_transaction = SerializerMethodField()
    my_today_transaction = SerializerMethodField()
    team_total_transaction = SerializerMethodField()
    team_today_transaction = SerializerMethodField()
    my_total_cards = SerializerMethodField()

    def get_parent(self, obj):
        if obj.parent_id < 0:
            return '无'
        parent = AgentModel.objects.get(pk=obj.parent_id)

        return parent.phone

    def get_subordinates_count(self, obj):
        records = AgentModel.objects.filter(parent_id=obj.pk)
        return records.count()

    def get_my_total_transaction(self, obj):
        records_recharge = RechargeModel.objects.filter(agent_id=obj.pk, status=1)

        result = 0

        for item in records_recharge:
            result += item.points

        return result

    def get_my_today_transaction(self, obj):
        today = datetime.datetime.now().date()
        records_recharge = RechargeModel.objects.filter(agent_id=obj.pk, status=1, create_time__gte=today)

        result = 0

        for item in records_recharge:
            result += item.points

        return result

    def get_team_total_transaction(self, obj):
        records_lv1_agent = AgentModel.objects.filter(parent_id=obj.pk)

        result = 0
        for lv1_item in records_lv1_agent:
            lv1_recharges = RechargeModel.objects.filter(agent_id=lv1_item.pk, status=1)
            for lv1_recharge in lv1_recharges:
                result += lv1_recharge.points

            records_lv2_agent = AgentModel.objects.filter(parent_id=lv1_item.pk)
            for lv2_item in records_lv2_agent:
                lv2_recharges = RechargeModel.objects.filter(agent_id=lv2_item.pk, status=1)
                for lv2_recharge in lv2_recharges:
                    result += lv2_recharge.points

                records_lv3_agent = AgentModel.objects.filter(parent_id=lv2_item.pk)
                for lv3_item in records_lv3_agent:
                    lv3_recharges = RechargeModel.objects.filter(agent_id=lv3_item.pk, status=1)
                    for lv3_recharge in lv3_recharges:
                        result += lv3_recharge.points

        return result

    def get_team_today_transaction(self, obj):
        today = datetime.datetime.now().date()
        records_lv1_agent = AgentModel.objects.filter(parent_id=obj.pk)

        result = 0
        for lv1_item in records_lv1_agent:
            lv1_recharges = RechargeModel.objects.filter(agent_id=lv1_item.pk, status=1, create_time__gte=today)
            for lv1_recharge in lv1_recharges:
                result += lv1_recharge.points

            records_lv2_agent = AgentModel.objects.filter(parent_id=lv1_item.pk)
            for lv2_item in records_lv2_agent:
                lv2_recharges = RechargeModel.objects.filter(agent_id=lv2_item.pk, status=1, create_time__gte=today)
                for lv2_recharge in lv2_recharges:
                    result += lv2_recharge.points

                records_lv3_agent = AgentModel.objects.filter(parent_id=lv2_item.pk)
                for lv3_item in records_lv3_agent:
                    lv3_recharges = RechargeModel.objects.filter(agent_id=lv3_item.pk, status=1, create_time__gte=today)
                    for lv3_recharge in lv3_recharges:
                        result += lv3_recharge.points

        return result

    def get_my_total_cards(self, obj):
        records_card = CardModel.objects.filter(agent_id=obj.pk)

        return records_card.count()

    class Meta:
        model = AgentModel
        exclude = ['password']
