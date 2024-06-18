from django.db import models


class BackstageUser(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=16)
    last_login = models.DateTimeField(null=True)

    class Meta:
        db_table = 'backstage_user'

    def save(self, *args, **kwargs):
        import hashlib
        md5 = hashlib.md5()
        md5.update(self.password.encode())
        self.password = md5.hexdigest()
        super(BackstageUser, self).save(*args, **kwargs)
