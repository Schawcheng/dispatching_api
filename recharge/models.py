from django.db import models


class RechargeModel(models.Model):
    recharge_no = models.CharField(max_length=20)
    points = models.PositiveIntegerField()
    recharge_cert = models.TextField(max_length=2048, null=True, blank=True)

    # 0=>待审核 1=>审核通过 2=>未通过
    status = models.PositiveSmallIntegerField(default=0)
    agent_id = models.BigIntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recharge'
