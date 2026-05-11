import pandas as pd
from django.core.management.base import BaseCommand
from sheets.models import Sheet, User
from sheets.task_utils import set_task_status
import traceback


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
				user = User.objects.filter(auto_hour_ID=personnel_code).first() if personnel_code else None
				if not user and device_code:
					user = User.objects.filter(auto_hour_ID=device_code).first()
				if not user:
					missing_info = {"name": row['نام'] + " " + row['نام خانوادگي'], "device_code": device_code}
					if missing_info not in not_founds:
						not_founds.append(missing_info)
					continue
				user_id = user.id
				date = str(row["تاريخ"])
				hours = row["مدت حضور"]
				parts = []
				for i in range(1, 6):  # i = 1..5
					entry = row[f'ورود {i}']
					exit = row[f'خروج {i}']
					if entry == 0 or exit ==0:
						break
					part = f"{entry.hour}:{entry.minute}-{exit.hour}:{exit.minute}"
					parts.append(part)
				attendance = '__'.join(parts)
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
				currentDayData["Attendance"] = attendance
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
