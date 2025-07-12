# myapp/migrations/0002_create_demo_user.py
from django.db import migrations
from django.contrib.auth import get_user_model


def create_demo_user(apps, schema_editor):
    User = get_user_model()
    User.objects.create_user(
        username="test@account.com", email="test@account.com", password="testpassword"
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]
    operations = [migrations.RunPython(create_demo_user)]
