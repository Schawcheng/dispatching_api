from django.db import models


class WithdrawModel(models.Model):
    withdraw_no = models.CharField(max_length=20)
    points = models.DecimalField(max_digits=10, decimal_places=2)

    user_id = models.BigIntegerField()
    is_agent = models.PositiveSmallIntegerField()

    # 1=>支付宝 2=>微信 3=>bank 4=>usdt
    payment_type = models.PositiveSmallIntegerField()

    # 0=>审核中 1=>审核通过 2=>审核未通过
    status = models.PositiveSmallIntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'withdraw'
