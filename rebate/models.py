from django.db import models


class RebateModel(models.Model):
    key = models.CharField(max_length=32)
    agent_id = models.BigIntegerField()
    customer_id = models.BigIntegerField()
    rebate_value = models.DecimalField(max_digits=10, decimal_places=2)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rebate'
