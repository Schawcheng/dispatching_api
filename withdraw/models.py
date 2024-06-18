from django.db import models


class Withdraw(models.Model):
    withdraw_no = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.PositiveSmallIntegerField()
    agent_id = models.BigIntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'withdraw'
