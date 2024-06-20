from django.db import models


class CardModel(models.Model):
    key = models.CharField(max_length=32)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # 0=>已发放 2=>回收中 3=>已核销
    status = models.PositiveSmallIntegerField()
    agent_id = models.BigIntegerField()
    customer_id = models.BigIntegerField(null=True, blank=True)

    expire = models.DateTimeField()

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'card'
