from rest_framework import serializers

from system_config.models import SystemConfigModel


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfigModel
        fields = '__all__'
