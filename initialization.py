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
    support = SystemConfigModel(title='tg_support', value='https://t.me/longgefacai', description='TG客服')
    receipt_address = SystemConfigModel(title='receipt_address', value='TLWPJubZL9eauXN9RbkPt9mguQm475CBm4', description='收款地址')
    out_rate = SystemConfigModel(title='out_rate', value='0.93', description='卖出折扣')
    in_rate = SystemConfigModel(title='in_rate', value='0.95', description='回收折扣')

    support.save()
    receipt_address.save()
    out_rate.save()
    in_rate.save()


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
    create_system_config()
    create_admin_account()

