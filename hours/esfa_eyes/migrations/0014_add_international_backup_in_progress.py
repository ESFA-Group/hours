from django.db import migrations
from esfa_eyes.models import (
    EsfaEyes,
    default_kavosh_series_sales_info,
    default_Captan_series_sales_info,
    default_MCM_series_sales_info,
)


def add_international_rows(apps, schema_editor):
    for record in EsfaEyes.objects.all():
        kavosh_defaults = default_kavosh_series_sales_info()
        if 'kavosh_series_sales_international_in_progress' not in record.kavosh_series_sales_info:
            record.kavosh_series_sales_info['kavosh_series_sales_international_in_progress'] = \
                kavosh_defaults['kavosh_series_sales_international_in_progress']

        captan_defaults = default_Captan_series_sales_info()
        if 'Captan_series_sales_international_in_progress' not in record.Captan_series_sales_info:
            record.Captan_series_sales_info['Captan_series_sales_international_in_progress'] = \
                captan_defaults['Captan_series_sales_international_in_progress']

        mcm_defaults = default_MCM_series_sales_info()
        if 'MCM_series_sales_international_not_deliverd' not in record.MCM_series_sales_info:
            record.MCM_series_sales_info['MCM_series_sales_international_not_deliverd'] = \
                mcm_defaults['MCM_series_sales_international_not_deliverd']
        if 'MCM_series_sales_international_in_progress' not in record.MCM_series_sales_info:
            record.MCM_series_sales_info['MCM_series_sales_international_in_progress'] = \
                mcm_defaults['MCM_series_sales_international_in_progress']

        record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('esfa_eyes', '0013_add_is_editable_to_json'),
    ]

    operations = [
        migrations.RunPython(
            add_international_rows,
        ),
    ]
