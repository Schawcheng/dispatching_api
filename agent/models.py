from django.db import models


class AgentModel(models.Model):
    phone = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    invitation_code = models.CharField(max_length=64, null=True)

    parent_id = models.BigIntegerField()

    points = models.PositiveIntegerField(default=0)

    usdt_address = models.TextField(max_length=1024, null=True)
    wechat_qrcode = models.TextField(max_length=1024, null=True)
    alipay_qrcode = models.TextField(max_length=1024, null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agent'

    def save(self, *args, **kwargs):
        import hashlib
        md5 = hashlib.md5()
        md5.update(self.password.encode('utf-8'))
        self.password = md5.hexdigest()
        super(AgentModel, self).save(*args, **kwargs)
