from django.db import models


class CardModel(models.Model):
    key = models.CharField(max_length=32)
    points = models.PositiveIntegerField()

    # 0=>已签发 1=>已售出 2=>回收中 3=>已核销 4=>回收被驳回
    status = models.PositiveSmallIntegerField(default=0)
    agent_id = models.BigIntegerField()
    customer_id = models.BigIntegerField(null=True, blank=True)

    # expire = models.DateTimeField()

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'card'
