from django.db import models


class CustomerModel(models.Model):
    phone = models.CharField(max_length=32)
    password = models.CharField(max_length=32)

    points = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    usdt_address = models.TextField(max_length=1024, null=True)
    wechat_qrcode = models.TextField(max_length=1024, null=True)
    alipay_qrcode = models.TextField(max_length=1024, null=True)
    bank = models.CharField(max_length=32, null=True)

    total_income = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer'

    def save(self, *args, **kwargs):
        import hashlib
        md5 = hashlib.md5()
        md5.update(self.password.encode())
        self.password = md5.hexdigest()
        super(CustomerModel, self).save(*args, **kwargs)
