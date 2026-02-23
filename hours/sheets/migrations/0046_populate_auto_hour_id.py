# Generated migration to populate auto_hour_ID field

from django.db import migrations

# Mapping: auto_hour_ID (key) -> user_id (value)
# Entries with value -1 are excluded as they represent invalid/unmatched users
AUTO_HOUR_ID_MAPPING = {
    1: 2,       # hassan, zahedi
    2: 12,      # Soheil, Safavi
    3: 17,      # Vahid, Hajihasani
    4: 22,      # ali reza, amiri
    5: 31,      # Morteza, Mansoori
    6: 19,      # Pooria, Allahkarami
    7: 9,       # Abbas, Torkamani
    8: 5,       # Hossein, Dadashi Ilkhechi
    9: 10,      # Ahmadreza, Darabi
    10: 11,     # Mohammadmahdi, Rajabi
    11: 4,      # MohammadHadi, Attarieh
    12: 6,      # Alireza, Mohammadi
    13: 3,      # Hamed, Morsali
    14: 1,      # Mohammad Rasoul, Noori
    15: 28,     # Mohsen, Ghasemi
    16: 15,     # Mohammad, Hajzaman
    17: 51,     # MASOUMEH, BAYAT
    18: 56,     # MirKazem, KhalifehZadeh
    19: 37,     # Hamid, Aslani
    20: 40,     # Gholam Reza, Moradi
    21: 42,     # Seyed Jalal, Asef Al hosseini
    22: 43,     # mohammad amin, sanei
    23: 48,     # Samira, Foroughi
    24: 68,     # Sina, Mohamadi
    25: 57,     # saeed, jaloo
    26: 49,     # samaneh, moslemi
    28: 50,     # Payam, Arabpour
    30: 83,     # Mehdi, Zebarjadi Zirak
    31: 81,     # Sajad, Banooie
    32: 84,     # Amir, EBADI
    33: 85,     # Mohammad, Malekan
    34: 74,     # Erfan, Riahi
    35: 86,     # Amin, Tavakoli
    36: 88,     # Hossein, Nakhostin
    37: 89,     # Niloofar, Moghadam
    38: 111,    # Taherkhani, Milad
    39: 90,     # Olad, Saeed
    42: 101,    # Kazemi, Yasin
    43: 93,     # rezaee, soheil
    44: 95,     # jahanbakhshi, mehrdad
    45: 113,    # sabori, mahla
    46: 119,    # hasanpoor, mohsen
    47: 118,    # khandani, mohadese
    48: 121,    # اسد زاده, علی
    49: 125,    # فاطمه ساعدي
    50: 122,    # محمد سعيد قنبري
    51: 126,    # اميرحسين اصلاحچي
    52: 120,    # رضا فرضي
    53: 124,    # محمد امين زينالي خامنه
    54: 128,    # محمد مهدي كريمي
    55: 130,    # مهوش عابدين پور
    56: 129,    # سيد عارف طباطبايي
    57: 45,     # فرجاد جعفري
    58: 57,     # سعيد جالو
    61: 133,    # مهسا نوروزی 
    62: 97,     # امید صادق زاده
    63: 132,    # حسين محمودي هاشمي
    64: 33,     # علي بهجتي مهرباني
    65: 9,      # عباس ترکماني
    66: 25,     # مصطفی رحمانی
    67: 56,     # میرکاظم خلیفه زاده 
    68: 73,     # معين عابديني
    69: 87,     # رضا اسفندياري
}


def populate_auto_hour_id(apps, schema_editor):
    """Populate auto_hour_ID field based on the mapping"""
    User = apps.get_model('sheets', 'User')
    
    for auto_hour_id, user_id in AUTO_HOUR_ID_MAPPING.items():
        try:
            user = User.objects.get(pk=user_id)
            user.auto_hour_ID = auto_hour_id
            user.save(update_fields=['auto_hour_ID'])
        except User.DoesNotExist:
            print(f"User with id {user_id} not found for auto_hour_ID {auto_hour_id}")


def reverse_populate(apps, schema_editor):
    """Reverse migration - set auto_hour_ID back to NULL"""
    User = apps.get_model('sheets', 'User')
    User.objects.all().update(auto_hour_ID=None)


class Migration(migrations.Migration):

    dependencies = [
        ('sheets', '0045_user_auto_hour_id'),
    ]

    operations = [
        migrations.RunPython(populate_auto_hour_id, reverse_populate),
    ]
