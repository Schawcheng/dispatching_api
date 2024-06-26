from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from agent.models import AgentModel


class AgentSerializer(serializers.ModelSerializer):
    parent = SerializerMethodField()
    subordinates_count = SerializerMethodField()

    def get_parent(self, obj):
        if obj.parent_id < 0:
            return '无上级'
        parent = AgentModel.objects.get(pk=obj.parent_id)

        return parent.phone

    def get_subordinates_count(self, obj):
        records = AgentModel.objects.filter(parent_id=obj.pk)
        return records.count()

    class Meta:
        model = AgentModel
        exclude = ['password']
