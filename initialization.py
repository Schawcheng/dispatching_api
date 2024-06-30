import os
import sys
import django

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dispatching_api.settings")

django.setup()

from backstage.models import BackstageUserModel

from system_config.models import SystemConfigModel


def create_admin_account():
    user = BackstageUserModel(username='kenshin', password="Wdnmd1314159...")
    user.save()


def create_system_config():
    lv1 = SystemConfigModel(title='lv1', value='0.20', description='一级反水率')
    lv2 = SystemConfigModel(title='lv2', value='0.10', description='二级反水率')
    lv3 = SystemConfigModel(title='lv3', value='0.05', description='三级反水率')
    support = SystemConfigModel(title='tg_support', value='https://t.me/longgefacai', description='TG客服')

    lv1.save()
    lv2.save()
    lv3.save()
    support.save()


def create_upload_dir():
    agent_qrcode = f'{base_dir}/upload/agent_qrcode'
    customer_qrcode = f'{base_dir}/upload/customer_qrcode'
    recharge_certs = f'{base_dir}/upload/recharge_certs'

    os.makedirs(agent_qrcode, mode=755, exist_ok=True)
    os.makedirs(customer_qrcode, mode=755, exist_ok=True)
    os.makedirs(recharge_certs, mode=755, exist_ok=True)

    os.chmod(agent_qrcode, mode=755)
    os.chmod(customer_qrcode, mode=755)
    os.chmod(recharge_certs, mode=755)


if __name__ == '__main__':
    create_upload_dir()
