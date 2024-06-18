from django.db import models


class Bank(models.Model):
    bank_name = models.CharField(max_length=128)
    bank_account = models.CharField(max_length=64)
    user_id = models.BigIntegerField()
    is_agent = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'bank'
