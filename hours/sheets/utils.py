from sheets.models import Project, Sheet, User, Food_data, Report, DailyReportSetting

class SheetUtils():
	@classmethod
	def normalize_sheet_weekday_data(cls, sheet):
		correct_weekdays = Sheet.empty_sheet_data(sheet.year, sheet.month)
		correct_weekdays_dict = {
			entry["Day"]: entry["WeekDay"] for entry in correct_weekdays
		}

		# Sync the length of sheet.data with correct_weekdays
		if len(sheet.data) > len(correct_weekdays):
			sheet.data = sheet.data[: len(correct_weekdays)]  # Truncate excess entries
		elif len(sheet.data) < len(correct_weekdays):
			# Duplicate the last entry and increment the day value to fill in the missing data
			for _ in range(len(sheet.data), len(correct_weekdays)):
				last_entry = sheet.data[-1]
				new_entry = last_entry.copy()
				new_entry["Day"] += 1
				new_entry["WeekDay"] = None  # We'll update WeekDay after this
				sheet.data.append(new_entry)

		for entry in sheet.data:
			entry["WeekDay"] = correct_weekdays_dict[entry["Day"]]
		sheet.save()