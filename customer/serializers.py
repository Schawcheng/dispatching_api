from rest_framework import serializers

from customer.models import CustomerModel


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerModel
        exclude = ['password', 'create_time', 'update_time']