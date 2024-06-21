import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dispatching_api.settings")

django.setup()

from backstage.models import BackstageUserModel


def create_admin_account():
    user = BackstageUserModel(username='admin', password="Wdnmd1314159...")
    user.save()


def create_upload_dir():
    pass


if __name__ == '__main__':
    create_admin_account()
