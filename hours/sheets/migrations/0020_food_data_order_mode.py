# Generated by Django 4.0.4 on 2024-07-07 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sheets', '0019_sheet_food_reduction_user_food_reduction'),
    ]

    operations = [
        migrations.AddField(
            model_name='food_data',
            name='order_mode',
            field=models.IntegerField(choices=[(0, 'disablePastDays'), (1, 'free'), (2, 'disableWholeWeek')], default=0, verbose_name='order_mode'),
        ),
    ]
