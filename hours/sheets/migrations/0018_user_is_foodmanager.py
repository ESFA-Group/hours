# Generated by Django 4.0.4 on 2024-06-23 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sheets', '0017_fooddata'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_FoodManager',
            field=models.BooleanField(default=False, verbose_name='is_FoodManager'),
        ),
    ]