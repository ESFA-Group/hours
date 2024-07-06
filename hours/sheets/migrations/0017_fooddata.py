# Generated by Django 4.0.4 on 2024-06-04 13:01

from django.db import migrations, models
import sheets.models


class Migration(migrations.Migration):

    dependencies = [
        ('sheets', '0016_sheet_food_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='Food_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField(default=sheets.models.current_year, verbose_name='year')),
                ('month', models.PositiveIntegerField(default=sheets.models.current_month, verbose_name='month')),
                ('data', models.JSONField(default=list)),
            ],
        ),
    ]
