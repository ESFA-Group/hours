import pandas as pd
from django.core.management.base import BaseCommand
from sheets.models import Sheet, User

USER_ID_MAP = {
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
	15: 28,     #Mohsen, Ghasemi
	16: 15,     #Mohammad, Hajzaman
	17: 51,     #MASOUMEH, BAYAT
	18: 56,     #MirKazem, KhalifehZadeh
	19: 37,     #Hamid, Aslani
	20: 40,     #Gholam Reza, Moradi
	21: 42,     #Seyed Jalal, Asef Al hosseini
	22: 43,     #mohammad amin, sanei
	23: 48,     #Samira, Foroughi
	24: 68,     #Sina, Mohamadi
	25: 57,     #saeed, jaloo
	26: 49,     #samaneh, moslemi
	27: -1,     #ali, maghsoudi 
	28: 50,     #Payam, Arabpour
	29: -1,     #Seyed Amir,    Hosseini
	30: 83,     #Mehdi, Zebarjadi Zirak
	31: 81,     #Sajad, Banooie
	32: 84,     #Amir, EBADI
	33: 85,     #Mohammad, Malekan
    34: 74,     #Erfan, Riahi
	35: 86,     #Amin, Tavakoli
	36: 88,     #Hossein, Nakhostin
	37: 89,     #Niloofar, Moghadam
	38: ,     #Taherkhani, Milad
	39: ,     #Olad, Saeed
	41: ,     #Saboor, hassan
	42: ,     #Kazemi, Yasin
	43: ,     #rezaee, soheil
	44: ,     #jahanbakhshi, mehrdad
	45: ,     #sabori, mahla
	46: ,     #hasanpoor, mohsen
	47: ,     #khandani, mohadese
	48: ,     #اسد زاده, علی
	49: ,     # فاطمه	ساعدي
	50: ,     # محمد سعيد	قنبري
	51: ,     # اميرحسين	اصلاحچي
	52: ,     # رضا	فرضي
	53: ,     # محمد امين	زينالي خامنه
    54: ,     # محمد مهدي	كريمي
    55: ,     # مهوش	عابدين پور
    56: ,     # سيد عارف	طباطبايي
    57: ,     # فرجاد	جعفري
    58: ,     # سعيد	جالو
}


class Command(BaseCommand):
    help = 'Import hours from Excel file and update Sheet records.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')
        parser.add_argument('year', type=str, help='Year')
        parser.add_argument('month', type=str, help='Month')

    def handle(self, *args, **options):
        file_path = options['file_path']
        year = options['year']
        month = options['month']
        df = pd.read_excel(file_path)
        df.fillna(0, inplace=True)
        not_founds = []
        current_sheet = None
        for index, row in df.iterrows():
            try:
                user_id = USER_ID_MAP[row["کد پرسنلي"] | row["کد در دستگاه"]]
            except Exception:
                if row["نام خانوادگي"] not in not_founds:
                    not_founds.append(row["نام خانوادگي"])
                continue
            date = row["تاريخ"]
            hours = row["مدت کارکرد"]
            y = date.split('/')[0]
            m = date.split('/')[1]
            if int(month) != int(m) or year != y:
                self.stdout.write(self.style.ERROR('year or month is not match'))
                continue
            d = int(date.split('/')[2])
            if current_sheet is None or current_sheet.user_id != user_id:
                if user_id == -1:
                    continue
                current_sheet = Sheet.objects.get(user_id=user_id, year=year, month=month)
                current_sheet.normalize_sheet()
            currentDayData = current_sheet.data[d-1]
            currentDayData["Auto Hours"] = f"{hours.hour}:{hours.minute}"
            current_sheet.save()
        self.stdout.write(self.style.SUCCESS(f"Import finished. Users not found: {not_founds}"))
