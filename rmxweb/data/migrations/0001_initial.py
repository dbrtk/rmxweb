# Generated by Django 4.0.6 on 2022-07-23 08:38

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('container', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('containerid', models.CharField(max_length=250)),
                ('url', models.TextField(null=True, validators=[django.core.validators.URLValidator()])),
                ('hostname', models.CharField(max_length=500, null=True)),
                ('seed', models.BooleanField(default=False)),
                ('file_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('file_path', models.CharField(blank=True, max_length=500, null=True)),
                ('title', models.TextField(blank=True, null=True)),
                ('hash_text', models.CharField(blank=True, max_length=128, null=True)),
                ('container', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='container.container')),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('url', models.TextField(null=True, validators=[django.core.validators.URLValidator()])),
                ('hostname', models.CharField(max_length=500, null=True)),
                ('data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.data')),
            ],
        ),
    ]
