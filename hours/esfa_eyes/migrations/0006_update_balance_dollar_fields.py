from django.db import migrations
from esfa_eyes.models import EsfaEyes

def update_balance_dollar_fields(apps, schema_editor):    
    dic_key_map = {
        "مقدار 1": "مقدار 1 (S1)",
        "مقدار 2": "مقدار 2 (S2)",
        "مقدار 3": "مقدار 3 (T)", 
        "مقدار 4": "مقدار 4 (Z)",
        "مقدار 5": "مقدار 5 (M)",
        "مقدار کل": "توضیحات",
    }
    
    for record in EsfaEyes.objects.all():        
        # Check if the structure exists
        if (hasattr(record, 'international_finance_info') and 
            record.international_finance_info and 
            'balance_dollars' in record.international_finance_info and 
            "_info" in record.international_finance_info['balance_dollars']):
            
            info_dict = record.international_finance_info['balance_dollars']["_info"]
            
            # Update keys while preserving values
            for old_key, new_key in dic_key_map.items():
                if old_key in info_dict:
                    info_dict[new_key] = info_dict.pop(old_key)
            
            record.save()


class Migration(migrations.Migration):
    dependencies = [
        ('esfa_eyes', '0005_add_user_access_to_eyes'),
    ]
    
    operations = [
        migrations.RunPython(
            update_balance_dollar_fields,
        ),
    ]