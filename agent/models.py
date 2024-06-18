from django.db import models


class AgentModel(models.Model):
    phone = models.CharField(max_length=32)
    password = models.CharField(max_length=16)

    parent_id = models.BigIntegerField()

    points = models.PositiveIntegerField(default=0)

    usdt_address = models.TextField(max_length=1024)
    wechat_qrcode = models.TextField(max_length=1024)
    alipay_qrcode = models.TextField(max_length=1024)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agent'

    def save(self, *args, **kwargs):
        import hashlib
        md5 = hashlib.md5()
        md5.update(self.password.encode())
        self.password = md5.hexdigest()
        super(AgentModel, self).save(*args, **kwargs)


class AgentRebateRateModel(models.Model):
    lv1 = models.DecimalField(max_digits=5, decimal_places=2)
    lv2 = models.DecimalField(max_digits=5, decimal_places=2)
    lv3 = models.DecimalField(max_digits=5, decimal_places=2)
    is_enable = models.PositiveSmallIntegerField(default=True)

    class Meta:
        db_table = 'agent_fee_rate'
