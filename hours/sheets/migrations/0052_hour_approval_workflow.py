# Generated manually for the multi-level hour approval workflow.
# If your real app already has migrations after 0001, rename this file and update
# the dependency to your latest migration before running migrate.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def forwards(apps, schema_editor):
    Sheet = apps.get_model('sheets', 'Sheet')
    for sheet in Sheet.objects.select_related('user').all().iterator():
        sheet.manager_level_1_verified = bool(sheet.is_verified)
        sheet.manager_level_2_verified = False
        sheet.supreme_verified = bool(sheet.is_supreme_verified)
        if sheet.user_id and hasattr(sheet.user, 'payment_type'):
            sheet.payment_type = sheet.user.payment_type or 'hours'
        sheet.save(update_fields=[
            'manager_level_1_verified',
            'manager_level_2_verified',
            'supreme_verified',
            'payment_type',
        ])


def backwards(apps, schema_editor):
    Sheet = apps.get_model('sheets', 'Sheet')
    for sheet in Sheet.objects.all().iterator():
        sheet.is_verified = bool(sheet.manager_level_1_verified and sheet.manager_level_2_verified)
        sheet.is_supreme_verified = bool(sheet.supreme_verified)
        sheet.save(update_fields=['is_verified', 'is_supreme_verified'])


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sheets', '0051_add_attendance'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='payment_type',
            field=models.CharField(
                choices=[('const', 'ثابت'), ('por', 'پورسانت'), ('hours', 'ساعتی'), ('work', 'وزارت کار')],
                default='hours',
                max_length=10,
                verbose_name='payment_type',
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='manager_level_1',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='managed_as_level_1',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='manager_level_2',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='managed_as_level_2',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='sheet',
            name='manager_level_1_verified',
            field=models.BooleanField(default=False, verbose_name='manager_level_1_verified'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='manager_level_2_verified',
            field=models.BooleanField(default=False, verbose_name='manager_level_2_verified'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='supreme_verified',
            field=models.BooleanField(default=False, verbose_name='supreme_verified'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='manager_level_1_verified_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='manager_level_1_verified_at'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='manager_level_2_verified_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='manager_level_2_verified_at'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='supreme_verified_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='supreme_verified_at'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='manager_level_1_verified_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='manager_level_1_verified_sheets',
                to=settings.AUTH_USER_MODEL,
                verbose_name='manager_level_1_verified_by',
            ),
        ),
        migrations.AddField(
            model_name='sheet',
            name='manager_level_2_verified_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='manager_level_2_verified_sheets',
                to=settings.AUTH_USER_MODEL,
                verbose_name='manager_level_2_verified_by',
            ),
        ),
        migrations.AddField(
            model_name='sheet',
            name='supreme_verified_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='supreme_verified_sheets',
                to=settings.AUTH_USER_MODEL,
                verbose_name='supreme_verified_by',
            ),
        ),
        migrations.AddField(
            model_name='sheet',
            name='last_rejected_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='rejected_sheets',
                to=settings.AUTH_USER_MODEL,
                verbose_name='last_rejected_by',
            ),
        ),
        migrations.AddField(
            model_name='sheet',
            name='last_rejected_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last_rejected_at'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='rejection_reason',
            field=models.TextField(blank=True, default='', verbose_name='rejection_reason'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='manager_level_1_comment',
            field=models.TextField(blank=True, default='', verbose_name='manager_level_1_comment'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='manager_level_2_comment',
            field=models.TextField(blank=True, default='', verbose_name='manager_level_2_comment'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='note_hours',
            field=models.TextField(blank=True, default='', verbose_name='note_hours'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='payment_type',
            field=models.CharField(
                choices=[('const', 'ثابت'), ('por', 'پورسانت'), ('hours', 'ساعتی'), ('work', 'وزارت کار')],
                default='hours',
                max_length=10,
                verbose_name='payment_type',
            ),
        ),
        migrations.RunPython(forwards, backwards),
    ]