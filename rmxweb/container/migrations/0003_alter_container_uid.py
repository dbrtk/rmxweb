# Generated by Django 3.2 on 2021-05-03 11:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('container', '0002_auto_20210429_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='container',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]