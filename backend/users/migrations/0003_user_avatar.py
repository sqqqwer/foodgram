# Generated by Django 5.1.4 on 2025-01-11 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_subscribe_delete_subscride_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default=1, upload_to='user/', verbose_name='Аватар'),
            preserve_default=False,
        ),
    ]
