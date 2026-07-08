from django.db import models
from django.contrib.auth.models import AbstractUser

import pandas as pd
import jdatetime as jdt


def user_directory_path(instance, filename) -> str:
	# file will be uploaded to MEDIA_ROOT/personal/username/<filename>
	return f"personal/{instance.username}/{filename}"


class User(AbstractUser):
	first_name_p = models.CharField("first name persian", max_length=150, blank=True)
	last_name_p = models.CharField("last name persian", max_length=150, blank=True)
	
	# payment info
	wage = models.IntegerField("wage", default=0)
	base_payment = models.IntegerField("base_payment", default=0)
	reduction1 = models.IntegerField("reduction1", default=0)
	reduction2 = models.IntegerField("reduction2", default=0)
	reduction3 = models.IntegerField("reduction3", default=0)
	food_reduction = models.IntegerField("food_reduction", default=0)
	addition1 = models.IntegerField("addition", default=0)
	addition2 = models.IntegerField("addition2", default=0)	
	comment = models.TextField("comment", default="", blank=True)
	payment_type_choices = [
		("const", "ثابت"),
		("por", "پورسانت"),
		("hours", "ساعتی"),
		("work", "وزارت کار"),
	]
	payment_type = models.CharField(
		"payment_type",
		max_length=10,
		choices=payment_type_choices,
		default="hours",
	)

	manager_level_1 = models.ForeignKey(
		"self",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="managed_as_level_1",
	)
	manager_level_2 = models.ForeignKey(
		"self",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="managed_as_level_2",
	)
	
	# access info
	is_ProjectReportManager = models.BooleanField("is_ProjectReportManager", default=False)
	is_SubReportManager = models.BooleanField("is_SubReportManager", default=False)
	is_MainReportManager = models.BooleanField("is_MainReportManager", default=False)
	is_HourVerifier = models.BooleanField("is_HourVerifier", default=False)
	is_SupremeHourVerifier = models.BooleanField("is_SupremeHourVerifier", default=False)
	is_FoodManager = models.BooleanField("is_FoodManager", default=False)
	is_PaymentManager = models.BooleanField("is_PaymentManager", default=False)
	# access to esfa eyes sheets
	is_staff_info_viewer = models.BooleanField("is_staff_info_viewer", default=False)
	is_detailed_sales_viewer = models.BooleanField("is_detailed_sales_viewer", default=False)
	is_global_sales_viewer = models.BooleanField("is_global_sales_viewer", default=False)
	# access to esfa eyes tables
	is_FinancialManager = models.BooleanField("is_FinancialManager", default=False)
	is_FinancialManager_readonly = models.BooleanField("is_FinancialManager_readonly", default=False)
	is_InternationalFinanceManager = models.BooleanField("is_InternationalFinanceManager", default=False)
	is_InternationalFinanceManager_readonly = models.BooleanField("is_InternationalFinanceManager_readonly", default=False)
	is_InternationalSalesManager = models.BooleanField("is_InternationalSalesManager", default=False)
	is_InternationalSalesManager_readonly = models.BooleanField("is_InternationalSalesManager_readonly", default=False)
	is_ProductionManager = models.BooleanField("is_ProductionManager", default=False)
	is_ProductionManager_readonly = models.BooleanField("is_ProductionManager_readonly", default=False)
	is_KiaProductionManager = models.BooleanField("is_KiaProductionManager", default=False)
	is_KiaProductionManager_readonly = models.BooleanField("is_KiaProductionManager_readonly", default=False)
	is_KavoshProductionManager = models.BooleanField("is_KavoshProductionManager", default=False)
	is_KavoshProductionManager_readonly = models.BooleanField("is_KavoshProductionManager_readonly", default=False)
	
	# group tags for verification
	staff_group_tag = models.PositiveSmallIntegerField("staff_group_tag", default=1)
	verifier_group_tags = models.CharField("verifier_group_tags", max_length=255, blank=True, default="", help_text="Comma-separated tags this verifier can see")

	# personal info
	auto_hour_ID = models.IntegerField("auto_hour_ID", null=True, blank=True)
	is_active = models.BooleanField("is_active", default=True)
	national_ID = models.CharField("national_ID", max_length=10, blank=True, default="")
	mobile1 = models.CharField("mobile1", max_length=11, blank=True, default="")
	mobile2 = models.CharField("mobile2", max_length=11, blank=True, default="")
	emergency_phone = models.CharField(
		"emergency_phone", max_length=11, blank=True, default=""
	)
	address = models.TextField("address", max_length=100, blank=True, default="")
	laptop_info = models.CharField(
		"laptop_info", max_length=100, blank=True, default=""
	)
	dob = models.CharField("date_of_birth", max_length=10, blank=True, default="")

	# bank info
	bank_name = models.CharField("bank_name", max_length=20, blank=True, default="")
	card_number = models.CharField("card_number", max_length=16, blank=True, default="")
	account_number = models.CharField(
		"account_number", max_length=13, blank=True, default=""
	)
	SHEBA_number = models.CharField(
		"SHEBA_number", max_length=26, blank=True, default=""
	)

	# document files
	personal_image = models.ImageField(
		"personal_image", upload_to=user_directory_path, blank=True
	)
	national_ID_front_image = models.ImageField(
		"national_ID_front", upload_to=user_directory_path, blank=True
	)
	national_ID_back_image = models.ImageField(
		"national_ID_back", upload_to=user_directory_path, blank=True
	)
	birth_cert_first_page = models.ImageField(
		"birth_cert_first_page", upload_to=user_directory_path, blank=True
	)
	birth_cert_changes_page = models.ImageField(
		"birth_cert_changes_page", upload_to=user_directory_path, blank=True
	)
	student_card = models.ImageField(
		"student_card", upload_to=user_directory_path, blank=True
	)
	military_service_card = models.ImageField(
		"military_service_card", upload_to=user_directory_path, blank=True
	)

	def __str__(self):
		return self.get_full_name()

	def check_info(self) -> bool:
		value_list = [
			"first_name",
			"last_name",
			"national_ID",
			"dob",
			"email",
			"mobile1",
			"address",
			"emergency_phone",
			"bank_name",
			"card_number",
			"account_number",
			"SHEBA_number",
			"personal_image",
			"national_ID_front_image",
			"national_ID_back_image",
			"birth_cert_first_page",
			"birth_cert_changes_page",
		]
		values = User.objects.filter(pk=self.id).values(*value_list).first()
		filled = all(list(values.values()))
		return filled

	def get_payment_info(self) -> dict:
		info = {
			"wage": self.wage,
			"basePayment": self.base_payment,
			"reduction1": self.reduction1,
			"reduction2": self.reduction2,
			"reduction3": self.reduction3,
			"food_reduction": self.food_reduction,
			"addition1": self.addition1,
			"addition2": self.addition2,
			"paymentType": self.payment_type,
		}
		return info


def current_year() -> int:
	return jdt.date.today().year


def current_month() -> int:
	return jdt.date.today().month


def current_day() -> int:
	return jdt.date.today().day


def current_mont_days(month: int, isleap: bool) -> int:
	"""gets a month and returns that date's month days number with leap year consideration
	(for jalali months)"""

	days_num = jdt.j_days_in_month[month - 1]
	if month == 12 and isleap:
		days_num += 1
	return days_num

def get_persian_weekday(jalali_date):
	"""Convert jalali date to Persian weekday name"""

	weekdays = {
		0: "شنبه",
		1: "یکشنبه", 
		2: "دوشنبه",
		3: "سه شنبه",
		4: "چهارشنبه",
		5: "پنجشنبه",
		6: "جمعه"
	}
	return weekdays[jalali_date.weekday()]


class Sheet(models.Model):
	payment_status_choices = [
		(0, "Not Paid"),
		(1, "Only Base Paid"),
		(2, "Only Complementary Paid"),
		(3, "Base+Complementary Paid"),
		(4, "Refund Needed"),
		(5, "Refund Paid"),
	]
	user = models.ForeignKey(
		User,
		verbose_name="user",
		related_name="sheets",
		on_delete=models.SET_NULL,
		null=True,
	)
	user_name = models.CharField("name", max_length=50, blank=True, default="")
	year = models.PositiveIntegerField("year", default=current_year)
	month = models.PositiveIntegerField("month", default=current_month)
	data = models.JSONField(default=list)
	food_data = models.JSONField(default=list, blank=True)
	mean = models.PositiveIntegerField("mean", default=0)  # in minutes
	total = models.PositiveIntegerField("total", default=0)  # in minutes
	submitted = models.BooleanField("submitted", default=False)
	is_verified = models.BooleanField("is_verified", default=False)
	is_supreme_verified = models.BooleanField("is_supreme_verified", default=False)

	# New multi-level approval workflow. Legacy fields above are intentionally kept
	# for backward compatibility and are synchronized by the API actions.
	manager_level_1_verified = models.BooleanField("manager_level_1_verified", default=False)
	manager_level_2_verified = models.BooleanField("manager_level_2_verified", default=False)
	supreme_verified = models.BooleanField("supreme_verified", default=False)
	manager_level_1_verified_at = models.DateTimeField("manager_level_1_verified_at", null=True, blank=True)
	manager_level_2_verified_at = models.DateTimeField("manager_level_2_verified_at", null=True, blank=True)
	supreme_verified_at = models.DateTimeField("supreme_verified_at", null=True, blank=True)
	manager_level_1_verified_by = models.ForeignKey(
		User,
		verbose_name="manager_level_1_verified_by",
		related_name="manager_level_1_verified_sheets",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
	)
	manager_level_2_verified_by = models.ForeignKey(
		User,
		verbose_name="manager_level_2_verified_by",
		related_name="manager_level_2_verified_sheets",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
	)
	supreme_verified_by = models.ForeignKey(
		User,
		verbose_name="supreme_verified_by",
		related_name="supreme_verified_sheets",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
	)
	last_rejected_by = models.ForeignKey(
		User,
		verbose_name="last_rejected_by",
		related_name="rejected_sheets",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
	)
	last_rejected_at = models.DateTimeField("last_rejected_at", null=True, blank=True)
	rejection_reason = models.TextField("rejection_reason", default="", blank=True)
	manager_level_1_comment = models.TextField("manager_level_1_comment", default="", blank=True)
	manager_level_2_comment = models.TextField("manager_level_2_comment", default="", blank=True)
	note_hours = models.TextField("note_hours", default="", blank=True)
	payment_type = models.CharField(
		"payment_type",
		max_length=10,
		choices=User.payment_type_choices,
		default="hours",
	)

	payment_status = models.IntegerField(
		"payment_status", choices=payment_status_choices, default=0
	)

	# payment info: data comes from user
	wage = models.IntegerField("wage", default=0)
	base_payment = models.IntegerField("base_payment", default=0)
	reduction1 = models.IntegerField("reduction1", default=0)
	reduction2 = models.IntegerField("reduction2", default=0)
	reduction3 = models.IntegerField("reduction3", default=0)
	food_reduction = models.IntegerField("food_reduction", default=0)
	addition1 = models.IntegerField("addition", default=0)
	addition2 = models.IntegerField("addition2", default=0)

	def __str__(self):
		return f"{self.user_name}_{self.year}_{self.month}"

	def save(self, *args, **kwargs):
		if not len(self.data):
			# Never persist a sheet with zero rows. Rebuild a blank grid for THIS
			# sheet's own period (not "today") so months viewed out of season keep
			# their correct days/weekdays. Fall back to the current month only if
			# year/month are somehow unusable.
			try:
				self.data = Sheet.empty_sheet_data(int(self.year), int(self.month))
			except (TypeError, ValueError):
				today = jdt.date.today()
				self.data = Sheet.empty_sheet_data(today.year, today.month)
		df = self.transform()
		self.mean = self.get_mean(df)
		self.total = self.get_total(df)
		super(Sheet, self).save(*args, **kwargs)

	def setup_sheet(self):
		self.month = int(self.month)
		self.year = int(self.year)
		self.user_name = self.user.get_full_name()
		self.wage = self.user.wage
		self.base_payment = self.user.base_payment
		self.reduction1 = self.user.reduction1
		self.reduction2 = self.user.reduction2
		self.reduction3 = self.user.reduction3
		self.food_reduction = self.user.food_reduction
		self.addition1 = self.user.addition1
		self.addition2 = self.user.addition2
		self.payment_type = self.user.payment_type
		self.save()

	@classmethod
	def empty_sheet_data(cls, year: int, month: int) -> list:
		is_leap = jdt.date(year, month, 1).isleap()
		days_num = current_mont_days(month, is_leap)
		data = [
			{
				"Day": day + 1,
				"WeekDay": jdt.date.j_weekdays_short_en[
					jdt.date(year, month, day + 1).weekday()
				],
				"Note Hours": "",
			}
			for day in range(days_num)
		]
		return data

	def hhmm2minutes(self, string: str) -> int:
		"""converter function
		convert string with hh:mm fromat to minutes
		"""
		try:
			h, m = string.split(":")
			return int(h) * 60 + int(m)
		except:
			return 0

	def minutes2hhmm(self, mins: int) -> str:
		h = mins // 60
		m = mins % 60
		return f"{h:02d}:{m:02d}"

	def parse_project_porp(self, string: str) -> int:
		try:
			return int(string.replace("%", "").strip()) / 100
		except:
			return 0

	def get_sheet_projects(self, df: pd.DataFrame) -> list:
		defaults = [
			"Day",
			"WeekDay",
			"Hours",
			"Auto Hours",
			"Remote",
			"Mission",
			"Forget",
			"Rest",
			"Total",
			"Attendance",
			"Description",
			"Note Hours",
		]
		projects = df.columns.difference(defaults)
		return list(projects)

	def transform(self) -> pd.DataFrame:
		"""transforms sheet data to a pandas DataFrame.
		all project cols and "Hours" col will contain minutes instead of hh:mm and percentage format
		"""
		df = pd.DataFrame(self.data)
		required = ["Auto Hours", "Remote", "Rest"]
		if not all(col in df.columns for col in required):
			return df

		# Older sheets predate these columns; treat missing ones as zero.
		optional = ["Mission", "Forget"]
		for col in optional:
			if col not in df.columns:
				df[col] = "00:00"

		projects = self.get_sheet_projects(df)

		for col in required + optional:
			df[col] = df[col].apply(self.hhmm2minutes).fillna(0)

		sum_components = (
			df["Auto Hours"] + df["Remote"] + df["Mission"] + df["Forget"] + df["Rest"]
		)

		if self.submitted and "Hours" in df:
			original_hours_converted = df["Hours"].apply(self.hhmm2minutes)
			computed_hours = (
				df["Auto Hours"] + df["Forget"] + df["Mission"] + df["Remote"] - df["Rest"]
			)
			df["Hours"] = original_hours_converted.where(sum_components == 0, computed_hours)
		else:
			df["Hours"] = (
				df["Auto Hours"] + df["Forget"] + df["Mission"] + df["Remote"] - df["Rest"]
			)

		df[projects] = (
			df[projects]
			.map(self.parse_project_porp)
			.apply(lambda col: col * df["Hours"])
		)
		return df

	def get_mean(self, df: pd.DataFrame) -> int:
		if "Hours" not in df.columns:
			return 0
		df = df.loc[df["Hours"] > 0]
		if not len(df):
			return 0
		return df["Hours"].sum() / len(df)

	def get_total(self, df: pd.DataFrame) -> int:
		if "Hours" not in df.columns:
			return 0
		return df["Hours"].sum()

	def get_base_payment(self) -> int:
		return self.base_payment

	def get_total_payment(self) -> int:
		hours = round(self.total / 60, 3)
		return hours * self.wage

	def get_final_payment(self) -> int:
		total_payment = self.get_total_payment()
		final_payment = (
			total_payment
			- (
				self.reduction1
				+ self.reduction2
				+ self.reduction3
				+ self.food_reduction
			)
			+ (self.addition1 + self.addition2)
		)
		return final_payment

	def get_complementary_payment(self) -> int:
		final_payment = self.get_final_payment()
		return final_payment - self.base_payment

	def get_payment_info(self) -> dict:
		info = {
			"wage": self.wage,
			"totalPayment": self.get_total_payment(),
			"basePayment": self.get_base_payment(),
			"reduction1": self.reduction1,
			"reduction2": self.reduction2,
			"reduction3": self.reduction3,
			"food_reduction": self.food_reduction,
			"addition1": self.addition1,
			"addition2": self.addition2,
			"finalPayment": self.get_final_payment(),
			"complementaryPayment": self.get_complementary_payment(),
			"paymentStatus": self.payment_status,
		}
		return info

	def get_public_payment_info(self) -> dict:
		info = {
			"basePayment": self.get_base_payment(),
			"complementaryPayment": self.get_complementary_payment(),
			"food_reduction": self.food_reduction,
			"paymentStatus": self.payment_status,
		}
		return info
	
	def normalize_sheet(self, should_normalize_weekday: bool = True):
		# Defensive: never index into or persist an empty grid. Callers validate
		# input, but if an empty list still reaches here, rebuild a blank month for
		# this sheet's period instead of crashing on all_data[0] or saving an empty
		# sheet.
		if not self.data:
			self.data = Sheet.empty_sheet_data(int(self.year), int(self.month))

		all_data = self.data

		if "Remote" not in all_data[0]:
			for data in all_data:
				# if "Hours" in data:
				# 	# Replace "Hours" with "Remote"
				# 	hours_value = data.pop("Hours")
				# 	data["Remote"] = hours_value
				# else:		
				data["Remote"] = "00:00"
				if "Auto Hours" not in data:
					data["Auto Hours"] = "00:00"
				data["Rest"] = "00:00"
		
		for data in all_data:
			if "Note Hours" not in data:
				data["Note Hours"] = ""
			# Older sheets predate Mission/Forget; back-fill so they persist.
			if "Mission" not in data:
				data["Mission"] = "00:00"
			if "Forget" not in data:
				data["Forget"] = "00:00"
			auto_m = self.hhmm2minutes(data.get("Auto Hours", "00:00"))
			rem_m = self.hhmm2minutes(data.get("Remote", "00:00"))
			mission_m = self.hhmm2minutes(data.get("Mission", "00:00"))
			forget_m = self.hhmm2minutes(data.get("Forget", "00:00"))
			rest_m = self.hhmm2minutes(data.get("Rest", "00:00"))
			data["Total"] = self.minutes2hhmm(
				auto_m + forget_m + mission_m + rem_m - rest_m
			)
		
		if should_normalize_weekday:
			self.normalize_sheet_weekday_data()
		self.save()


	def normalize_sheet_weekday_data(self):
		correct_weekdays = Sheet.empty_sheet_data(self.year, self.month)
		correct_weekdays_dict = {
			entry["Day"]: entry["WeekDay"] for entry in correct_weekdays
		}

		# Sync the length of sheet.data with correct_weekdays
		if len(self.data) > len(correct_weekdays):
			self.data = self.data[: len(correct_weekdays)]  # Truncate excess entries
		elif len(self.data) < len(correct_weekdays):
			# Duplicate the last entry and increment the day value to fill in the missing data
			for _ in range(len(self.data), len(correct_weekdays)):
				last_entry = self.data[-1]
				new_entry = last_entry.copy()
				new_entry["Day"] += 1
				new_entry["WeekDay"] = None  # We'll update WeekDay after this
				self.data.append(new_entry)

		for entry in self.data:
			entry["WeekDay"] = correct_weekdays_dict[entry["Day"]]
		self.save()


	def reset_approval_state(self):
		self.submitted = False
		self.manager_level_1_verified = False
		self.manager_level_2_verified = False
		self.supreme_verified = False
		self.manager_level_1_verified_at = None
		self.manager_level_2_verified_at = None
		self.supreme_verified_at = None
		self.manager_level_1_verified_by = None
		self.manager_level_2_verified_by = None
		self.supreme_verified_by = None
		self.is_verified = False
		self.is_supreme_verified = False

	@property
	def is_fully_approved(self) -> bool:
		return (
			self.submitted
			and self.manager_level_1_verified
			and self.manager_level_2_verified
			and self.supreme_verified
		)

	def sync_legacy_verification_fields(self):
		# Old code only had one manager flag. In the new workflow, old
		# is_verified is true only after both manager approvals are present.
		self.is_verified = self.manager_level_1_verified and self.manager_level_2_verified
		self.is_supreme_verified = self.supreme_verified


class ProjectFamily(models.Model):
	name = models.CharField("name", max_length=150)

	class Meta:
		verbose_name_plural = "Projec Families"

	def __str__(self):
		return self.name


class Project(models.Model):
	family = models.ForeignKey(
		ProjectFamily,
		verbose_name="family",
		related_name="projects",
		on_delete=models.SET_NULL,
		null=True,
	)
	name = models.CharField("name", max_length=150)

	def __str__(self):
		return f"{self.family.name}-{self.name}"


class Food_data(models.Model):
	food_order_mode = [
		(0, "disablePastDays"),
		(1, "free"),
		(2, "disableWholeWeek"),
	]
	year = models.PositiveIntegerField("year", default=current_year)
	month = models.PositiveIntegerField("month", default=current_month)
	order_mode = models.IntegerField("order_mode", choices=food_order_mode, default=0)
	data = models.JSONField(default=list)
	statistics_and_cost_data = models.JSONField(default=list)
	
	def __str__(self):
		return f"Food - {self.year}/{self.month}"

class Report(models.Model):
	user = models.ForeignKey(
		User,
		verbose_name="user",
		related_name="report",
		on_delete=models.SET_NULL,
		null=True,
	)
	year = models.PositiveIntegerField("year", default=current_year)
	month = models.PositiveIntegerField("month", default=current_month)
	day = models.PositiveIntegerField("day", default=current_day)
	content = models.TextField(default="")
	sub_comment = models.TextField(default="", blank=True)
	main_comment = models.TextField(default="", blank=True)
	manager_comment_hide_for_user = models.BooleanField(default=True)
	manager_comment_hide_for_supervisor = models.BooleanField(default=True)
	supervisor_comment_hide_for_user = models.BooleanField(default=True)

	def __str__(self):
		return f"Report by {self.user.username} on {self.year}/{self.month}/{self.day}"


class DailyReportSetting(models.Model):
	no_limit_submission = models.BooleanField(default=False)
	start_report_hour = models.PositiveIntegerField("start_report_hour", default=17)
	end_report_hour = models.PositiveIntegerField("end_report_hour", default=22)
