# Generated by Django 4.0.4 on 2024-05-27 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sheets', '0015_alter_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='sheet',
            name='food_data',
            field=models.JSONField(default=list),
        ),
    ]
