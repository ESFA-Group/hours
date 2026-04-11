from django.db import models
from .schemas import esfa_eyes_info as schemas
from .schemas.esfa_eyes_info import EsfaEyesInfo, EsfaEyesMonltyInfo, EsfaEyesProductInfo
from sheets.models import User
import copy

# sales access
access_mappings = {
	'financial_info': ['Amiri'],
	'international_finance_info': ['Zahedi'],
	'international_sales_info': ['Dadashi'],
	'products_info': ['Koolaji'],
	'kavosh_products_info': ['Koolaji'],
	'kia_products_info': ['Kazempourian'],
	'Captan_series_sales_info': [''],
	'kavosh_series_sales_info': [''],
	'MCM_series_sales_info': [''],
}

def default_financial_info():
	return {
		'balance_rials_official': EsfaEyesInfo(0, who_can_see=access_mappings["financial_info"]).__dict__,
		'balance_rials': EsfaEyesInfo(0, who_can_see=access_mappings["financial_info"]).__dict__,
		'montly_checks_received': EsfaEyesMonltyInfo(who_can_see=access_mappings["financial_info"]).__dict__,
		'montly_checks_issued': EsfaEyesMonltyInfo(who_can_see=access_mappings["financial_info"]).__dict__,
		'montly_installment': EsfaEyesMonltyInfo(who_can_see=access_mappings["financial_info"]).__dict__,
		'montly_total_sales': EsfaEyesMonltyInfo(update_interval_days=14, who_can_see=access_mappings["financial_info"]).__dict__,
		'individual_sales': EsfaEyesProductInfo(who_can_see=access_mappings["financial_info"]).__dict__,
		'individual_sales_quantities': EsfaEyesProductInfo(who_can_see=access_mappings["financial_info"]).__dict__,
		'individual_sales_total_received': EsfaEyesProductInfo(who_can_see=access_mappings["financial_info"]).__dict__,
		'individual_sales_check_received': EsfaEyesProductInfo(who_can_see=access_mappings["financial_info"]).__dict__,
		'individual_sales_unknown': EsfaEyesProductInfo(who_can_see=access_mappings["financial_info"]).__dict__,
		'total_insured_staffs': EsfaEyesInfo(0, 31, who_can_see=access_mappings["financial_info"]).__dict__,
		'total_insured_non_staffs': EsfaEyesInfo(0, 31, who_can_see=access_mappings["financial_info"]).__dict__,
		'total_uninsured_staffs': EsfaEyesInfo(0, 31, who_can_see=access_mappings["financial_info"]).__dict__,
		'total_salary_paid': EsfaEyesMonltyInfo(who_can_see=access_mappings["financial_info"]).__dict__,
		'total_insurance_paid': EsfaEyesMonltyInfo(who_can_see=access_mappings["financial_info"]).__dict__,
	}

def default_international_finance_info():
	return {     
		"balance_dollars": EsfaEyesProductInfo({
			"مقدار 1 (S1)": 0,
			"مقدار 2 (S2)": 0,
			"مقدار 3 (T)": 0, 
			"مقدار 4 (Z)": 0,
			"مقدار 5 (M)": 0,
			"توضیحات": 0,
			}, 2, who_can_see=access_mappings["international_finance_info"]).__dict__,
		"china_production_orders": EsfaEyesProductInfo(who_can_see=access_mappings["international_finance_info"]).__dict__,
	}

def default_international_sales_info():
	return {
		"montly_international_total_sales": EsfaEyesMonltyInfo(update_interval_days=14, who_can_see=access_mappings["international_sales_info"]).__dict__,
		# "international_individual_sales": EsfaEyesProductInfo(who_can_see=access_mappings["international_sales_info"]).__dict__,
		# "international_individual_sales_quantities": EsfaEyesProductInfo(who_can_see=access_mappings["international_sales_info"]).__dict__,
		"turkiye_inventory": EsfaEyesProductInfo(who_can_see=access_mappings["international_sales_info"]).__dict__,
	}

def default_products_info():
	return {
		"unproduced_workshop_inventory": EsfaEyesProductInfo({
				"Esfa Meter": 0,
				"Pishtaz": 0,
				"Other": 0,
			},update_interval_days=7, who_can_see=access_mappings["products_info"]).__dict__,
		"ready_products": EsfaEyesProductInfo({
				"Esfa Meter": 0,
				"Pishtaz": 0,
				"Other": 0,
			},update_interval_days=7, who_can_see=access_mappings["products_info"]).__dict__,
		"unproducable_shortage_product": EsfaEyesProductInfo({
				"Esfa Meter": 0,
				"Pishtaz": 0,
				"Other": 0,
			},update_interval_days=7, who_can_see=access_mappings["products_info"]).__dict__,
	}

def default_kia_products_info():
	return {
		"unproduced_kia_workshop_inventory": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=7, who_can_see=access_mappings["kia_products_info"]).__dict__,
		"ready_kia_products": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=7, who_can_see=access_mappings["kia_products_info"]).__dict__,
		"unproducable_shortage_kia_product": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=7, who_can_see=access_mappings["kia_products_info"]).__dict__,
		"deliverd_1404": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=7, who_can_see=access_mappings["kia_products_info"]).__dict__,
		"deliverd_1403": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=180, who_can_see=access_mappings["kia_products_info"]).__dict__,
		"deliverd_1402": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=180, who_can_see=access_mappings["kia_products_info"]).__dict__,
		"deliverd_1401": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=180, who_can_see=access_mappings["kia_products_info"]).__dict__,
		"deliverd_1400": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=180, who_can_see=access_mappings["kia_products_info"]).__dict__,
		"deliverd_1399": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=180, who_can_see=access_mappings["kia_products_info"]).__dict__,
	}

def default_kavosh_products_info():
	return {
		"unproduced_kavosh_workshop_inventory": EsfaEyesProductInfo({
				"T22": 0,
				"TDM": 0,
				"TEM": 0,
				"CM1": 0,
				"CB1": 0,
				"CAPTAN12": 0,
				"MCM": 0,
			},update_interval_days=7, who_can_see=access_mappings["kavosh_products_info"]).__dict__,
		"ready_kavosh_products": EsfaEyesProductInfo({
				"T22": 0,
				"TDM": 0,
				"TEM": 0,
				"CM1": 0,
				"CB1": 0,
				"CAPTAN12": 0,
				"MCM": 0,
			},update_interval_days=7, who_can_see=access_mappings["kavosh_products_info"]).__dict__,
		"unproducable_shortage_kavosh_product": EsfaEyesProductInfo({
				"T22": 0,
				"TDM": 0,
				"TEM": 0,
				"CM1": 0,
				"CB1": 0,
				"CAPTAN12": 0,
				"MCM": 0,
			},update_interval_days=7, who_can_see=access_mappings["kavosh_products_info"]).__dict__,
	}

# Sales

def default_Captan_series_sales_info():
	return {
		"Captan_series_sales_1404": EsfaEyesProductInfo({
				"Captan12": 21,
				"Inductan": 0,
			},update_interval_days=180, who_can_see=access_mappings["Captan_series_sales_info"]).__dict__,
		"Captan_series_sales_international": EsfaEyesProductInfo({
				"Captan12": 13,
				"Inductan": 0,
			},update_interval_days=180, who_can_see=access_mappings["Captan_series_sales_info"]).__dict__,
		"Captan_series_sales_international_not_delivered": EsfaEyesProductInfo({
				"Captan12": 12,
				"Inductan": 0,
			},update_interval_days=180, who_can_see=access_mappings["Captan_series_sales_info"]).__dict__,
	}

def default_kavosh_series_sales_info():
	return {
		"kavosh_series_sales_1399": EsfaEyesProductInfo({
				"Kavosh": 9,
				"TDM": 4,
				"SweechBox": 5,
				"CB1": 3,
				"CM1": 0,
			},update_interval_days=180, who_can_see=access_mappings["kavosh_series_sales_info"]).__dict__,
		"kavosh_series_sales_1400": EsfaEyesProductInfo({
				"Kavosh": 9,
				"TDM": 5,
				"SweechBox": 5,
				"CB1": 0,
				"CM1": 0,
			},update_interval_days=180, who_can_see=access_mappings["kavosh_series_sales_info"]).__dict__,
		"kavosh_series_sales_1401": EsfaEyesProductInfo({
				"Kavosh": 16,
				"TDM": 10,
				"SweechBox": 7,
				"CB1": 1,
				"CM1": 0,
			},update_interval_days=180, who_can_see=access_mappings["kavosh_series_sales_info"]).__dict__,
		"kavosh_series_sales_1402": EsfaEyesProductInfo({
				"Kavosh": 29,
				"TDM": 27,
				"SweechBox": 9,
				"CB1": 7,
				"CM1": 2,
			},update_interval_days=180, who_can_see=access_mappings["kavosh_series_sales_info"]).__dict__,
		"kavosh_series_sales_1403": EsfaEyesProductInfo({
				"Kavosh": 28,
				"TDM": 15,
				"SweechBox": 7,
				"CB1": 7,
				"CM1": 0,
			},update_interval_days=180, who_can_see=access_mappings["kavosh_series_sales_info"]).__dict__,
		"kavosh_series_sales_1404": EsfaEyesProductInfo({
				"Kavosh": 20,
				"TDM": 10,
				"SweechBox": 9,
				"CB1": 3,
				"CM1": 1,
			},update_interval_days=180, who_can_see=access_mappings["kavosh_series_sales_info"]).__dict__,
		"kavosh_series_sales_international": EsfaEyesProductInfo({
				"Kavosh": 17,
				"TDM": 6,
				"SweechBox": 10,
				"CB1":  1,
				"CM1": 5,
			},update_interval_days=180, who_can_see=access_mappings["kavosh_series_sales_info"]).__dict__,
		"kavosh_series_sales_international_not_deliverd": EsfaEyesProductInfo({
				"Kavosh": 4,
				"TDM": 1,
				"SweechBox": 1,
				"CB1": 1,
				"CM1": 1,
			},update_interval_days=180, who_can_see=access_mappings["kavosh_series_sales_info"]).__dict__,
	}

def default_MCM_series_sales_info():
	return {
		"MCM_series_sales_1402": EsfaEyesProductInfo({
				"MCM1": 1,
				"غیر فروش": 0,
			},update_interval_days=180, who_can_see=access_mappings["MCM_series_sales_info"]).__dict__,
		"MCM_series_sales_1403": EsfaEyesProductInfo({
				"MCM1": 6,
				"غیر فروش": 3,
			},update_interval_days=180, who_can_see=access_mappings["MCM_series_sales_info"]).__dict__,
		"MCM_series_sales_1404": EsfaEyesProductInfo({
				"MCM1": 9,
				"غیر فروش": 0,
			},update_interval_days=180, who_can_see=access_mappings["MCM_series_sales_info"]).__dict__,
		"MCM_series_sales_international": EsfaEyesProductInfo({
				"MCM1": 3,
				"غیر فروش": 1,
			},update_interval_days=180, who_can_see=access_mappings["MCM_series_sales_info"]).__dict__,
	}



class EsfaEyes(models.Model):
	year = models.CharField("year", max_length=4, default="1404")
	financial_info = models.JSONField(default=default_financial_info)
	international_finance_info = models.JSONField(default=default_international_finance_info)
	international_sales_info = models.JSONField(default=default_international_sales_info)
	products_info = models.JSONField(default=default_products_info)
	kavosh_products_info = models.JSONField(default=default_kavosh_products_info)
	kia_products_info = models.JSONField(default=default_kia_products_info)
	Captan_series_sales_info = models.JSONField(default=default_Captan_series_sales_info)
	kavosh_series_sales_info = models.JSONField(default=default_kavosh_series_sales_info)
	MCM_series_sales_info = models.JSONField(default=default_MCM_series_sales_info)

	def __str__(self):
		return f"ESFA Eyes - {self.year}"

	def __getitem__(self, key):
		return getattr(self, key)

	def get(self, user: User, editable=False):
		info = {}
		if not user:
			return info

		if user.is_superuser and not editable:
			info.update(self.financial_info)
			info.update(self.international_finance_info)
			info.update(self.international_sales_info)
			info.update(self.products_info)
			info.update(self.kavosh_products_info)
			info.update(self.kia_products_info)
			info.update(self.Captan_series_sales_info)
			info.update(self.kavosh_series_sales_info)
			info.update(self.MCM_series_sales_info)
			return info
		if user.is_FinancialManager or user.is_FinancialManager_readonly:
			info.update(self.financial_info)
		if user.is_InternationalFinanceManager or user.is_InternationalFinanceManager_readonly:
			info.update(self.international_finance_info)
		if user.is_InternationalSalesManager or user.is_InternationalSalesManager_readonly:
			info.update(self.international_sales_info)
		if user.is_ProductionManager or user.is_ProductionManager_readonly:
			info.update(self.products_info)
		if user.is_KavoshProductionManager or user.is_KavoshProductionManager_readonly:
			info.update(self.kavosh_products_info)
		if user.is_KiaProductionManager or user.is_KiaProductionManager_readonly:
			info.update(self.kia_products_info)
		if user.is_detailed_sales_viewer:
			info.update(self.Captan_series_sales_info)
			info.update(self.kavosh_series_sales_info)
			info.update(self.MCM_series_sales_info)

		return info

	def update_user_access(self):
		for field_name, users_list in access_mappings.items():
			field_data = getattr(self, field_name)
			if isinstance(field_data, dict):
				for key in field_data:
					if isinstance(field_data[key], dict):
						field_data[key]['who_can_see'] = users_list.copy()

				
				setattr(self, field_name, field_data)
