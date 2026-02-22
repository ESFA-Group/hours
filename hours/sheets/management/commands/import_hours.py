import pandas as pd
from django.core.management.base import BaseCommand
from sheets.models import Sheet, User
from sheets.task_utils import set_task_status
import traceback

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
	38: 111,     #Taherkhani, Milad ?
	39: 90,     #Olad, Saeed
	41: -1,     #Saboor, hassan
	42: 101,     #Kazemi, Yasin
	43: 93,     #rezaee, soheil
	44: 95,     #jahanbakhshi, mehrdad
	45: 113,     #sabori, mahla ?
	46: 119,     #hasanpoor, mohsen ?
	47: 118,     #khandani, mohadese
	48: 121,     #اسد زاده, علی
	49: 125,     # فاطمه	ساعدي
	50: 122,     # محمد سعيد	قنبري
	51: 126,     # اميرحسين	اصلاحچي
	52: 120,     # رضا	فرضي
	53: 124,     # محمد امين	زينالي خامنه
	54: 128,     # محمد مهدي	كريمي
	55: 130,     # مهوش	عابدين پور
	56: 129,     # سيد عارف	طباطبايي
	57: 45,     # فرجاد	جعفري
	58: 57,     # سعيد	جالو
	-1: 54,     # مهشید خیری
}


class Command(BaseCommand):
	help = 'Import hours from Excel file and update Sheet records.'

	def add_arguments(self, parser):
		parser.add_argument('file_path', type=str, help='Path to the Excel file')
		parser.add_argument('year', type=str, help='Year')
		parser.add_argument('month', type=str, help='Month')
		parser.add_argument('--task_id', type=str, help='Task ID for status tracking', required=False)

	def handle(self, *args, **options):
		task_id = options.get('task_id')
		try:
			file_path = options['file_path']
			year = options['year']
			month = options['month']
			df = pd.read_excel(file_path)
			df.fillna(0, inplace=True)
			not_founds = []
			imported_any = False
			current_sheet = None
			for index, row in df.iterrows():
				personnel_code = row.get("کد پرسنلي")
				device_code = row.get("کد در دستگاه")
				if personnel_code and personnel_code in USER_ID_MAP:
					user_id = USER_ID_MAP[personnel_code]
				elif device_code and device_code in USER_ID_MAP:
					user_id = USER_ID_MAP[device_code]
				else:
					missing_info = {"name": row['نام'] + " " + row['نام خانوادگي'], "device_code": device_code}
					if missing_info not in not_founds:
						not_founds.append(missing_info)
					continue
				date = str(row["تاريخ"])
				hours = row["مدت حضور"]
				y = date.split('/')[0]
				m = date.split('/')[1]
				if int(month) != int(m) or year != y:
					self.stdout.write(self.style.ERROR('year or month is not match'))
					continue
				d = int(date.split('/')[2])
				if current_sheet is None or current_sheet.user_id != user_id:
					if user_id == -1:
						continue
					current_sheet, created = Sheet.objects.get_or_create(user_id=user_id, year=year, month=month)
					if created:
						current_sheet.setup_sheet()

					current_sheet.normalize_sheet()
				currentDayData = current_sheet.data[d-1]
				currentDayData["Auto Hours"] = f"{hours.hour:02d}:{hours.minute:02d}"
				current_sheet.normalize_sheet()
				imported_any = True
			
			summary = f"Import finished. Users not found: {not_founds}"
			status = 'completed' if imported_any else 'error'
			if not imported_any:
				summary = f"Import failed: No matching data found for {year}/{month}."

			if task_id:
				set_task_status(task_id, status, summary, data={'users_not_found': not_founds})
			self.stdout.write(self.style.SUCCESS(summary))
		except Exception as e:
			error_msg = f"Import failed: {str(e)}"
			if task_id:
				set_task_status(task_id, 'error', error_msg, data={'traceback': traceback.format_exc()})
			self.stdout.write(self.style.ERROR(error_msg))
