from rest_framework import serializers

from bank.models import BankModel


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankModel
        fields = '__all__'
