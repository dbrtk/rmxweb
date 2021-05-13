# Generated by Django 3.2 on 2021-05-06 14:22

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20210429_1630'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='data',
            name='data_id',
        ),
        migrations.RemoveField(
            model_name='link',
            name='seed',
        ),
        migrations.AddField(
            model_name='data',
            name='url',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='hostname',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='data',
            name='file_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='data',
            name='file_path',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='data',
            name='hash_text',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='data',
            name='hostname',
            field=models.CharField(max_length=200, null=True),
        ),
    ]