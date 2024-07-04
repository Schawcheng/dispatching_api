from django.db import models


class CardModel(models.Model):
    card_no = models.CharField(max_length=32, null=True)
    key = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    points = models.PositiveIntegerField()
    discount = models.DecimalField(max_digits=4, decimal_places=2, null=True)

    # 0=>已签发 1=>已售出 2=>回收中 3=>已核销 4=>回收被驳回
    status = models.PositiveSmallIntegerField(default=0)
    agent_id = models.BigIntegerField()
    customer_id = models.BigIntegerField(null=True, blank=True)

    # expire = models.DateTimeField()

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'card'
