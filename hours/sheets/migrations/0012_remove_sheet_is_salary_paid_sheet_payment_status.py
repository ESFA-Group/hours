# Generated by Django 4.0.4 on 2024-05-19 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sheets', '0011_sheet_is_salary_paid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sheet',
            name='is_salary_paid',
        ),
        migrations.AddField(
            model_name='sheet',
            name='payment_status',
            field=models.IntegerField(choices=[(0, 'Not paid'), (1, 'Base paid'), (2, 'Completly paid')], default=0, verbose_name='payment_status'),
        ),
    ]
