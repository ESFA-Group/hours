# Generated by Django 4.0.4 on 2024-11-05 14:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sheets', '0023_alter_sheet_food_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='family',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects', to='sheets.projectfamily', verbose_name='family'),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_date', models.DateField()),
                ('content', models.TextField()),
                ('sub_comment', models.TextField()),
                ('main_comment', models.TextField()),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='report', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
    ]