from django.db import models


class BankModel(models.Model):
    username = models.CharField(max_length=128)
    bank_name = models.CharField(max_length=128)
    bank_account = models.CharField(max_length=64)
    register_bank = models.TextField(max_length=1024)
    user_id = models.BigIntegerField()
    is_agent = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'bank'
