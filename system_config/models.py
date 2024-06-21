from django.db import models


class SystemConfigModel(models.Model):
    title = models.CharField(max_length=128)
    value = models.TextField(max_length=4096)
    description = models.TextField(max_length=4096, null=True)

    class Meta:
        db_table = 'system_config'
