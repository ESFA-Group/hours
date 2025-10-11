from django.db import models
from .schemas import esfa_eyes_info as schemas
from .schemas.esfa_eyes_info import EsfaEyesInfo, EsfaEyesMonltyInfo, EsfaEyesProductInfo
from sheets.models import User
import copy

users_with_financial_info_access = ['Amiri']
users_with_international_finance_info = ['Zahedi']
users_with_international_sales_info = ['Dadashi']
users_with_products_info_access = ['Koolaji']
users_with_kavosh_products_info_access = ['Koolaji']
users_with_kia_products_info_access = ['Kazempourian']
access_mappings = {
	'financial_info': ['Amiri'],
	'international_finance_info': ['Zahedi'],
	'international_sales_info': ['Dadashi'],
	'products_info': ['Koolaji'],
	'kavosh_products_info': ['Koolaji'],
	'kia_products_info': ['Kazempourian']
}

def default_financial_info():
	return {
		'balance_rials_official': EsfaEyesInfo(0, who_can_see=users_with_financial_info_access).__dict__,
		'balance_rials': EsfaEyesInfo(0, who_can_see=users_with_financial_info_access).__dict__,
		'montly_checks_received': EsfaEyesMonltyInfo(who_can_see=users_with_financial_info_access).__dict__,
		'montly_checks_issued': EsfaEyesMonltyInfo(who_can_see=users_with_financial_info_access).__dict__,
		'montly_installment': EsfaEyesMonltyInfo(who_can_see=users_with_financial_info_access).__dict__,
		'montly_total_sales': EsfaEyesMonltyInfo(update_interval_days=14, who_can_see=users_with_financial_info_access).__dict__,
		'individual_sales': EsfaEyesProductInfo(who_can_see=users_with_financial_info_access).__dict__,
		'individual_sales_quantities': EsfaEyesProductInfo(who_can_see=users_with_financial_info_access).__dict__,
		'individual_sales_total_received': EsfaEyesProductInfo(who_can_see=users_with_financial_info_access).__dict__,
		'individual_sales_check_received': EsfaEyesProductInfo(who_can_see=users_with_financial_info_access).__dict__,
		'individual_sales_unknown': EsfaEyesProductInfo(who_can_see=users_with_financial_info_access).__dict__,
		'total_insured_staffs': EsfaEyesInfo(0, 31, who_can_see=users_with_financial_info_access).__dict__,
		'total_uninsured_staffs': EsfaEyesInfo(0, 31, who_can_see=users_with_financial_info_access).__dict__,
		'total_salary_paid': EsfaEyesMonltyInfo(who_can_see=users_with_financial_info_access).__dict__,
		'total_insurance_paid': EsfaEyesMonltyInfo(who_can_see=users_with_financial_info_access).__dict__,
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
			}, 2, who_can_see=users_with_international_finance_info).__dict__,
		"china_production_orders": EsfaEyesProductInfo(who_can_see=users_with_international_finance_info).__dict__,
	}

def default_international_sales_info():
	return {
		"montly_international_total_sales": EsfaEyesMonltyInfo(update_interval_days=14, who_can_see=users_with_international_sales_info).__dict__,
		# "international_individual_sales": EsfaEyesProductInfo(who_can_see=users_with_international_sales_info).__dict__,
		# "international_individual_sales_quantities": EsfaEyesProductInfo(who_can_see=users_with_international_sales_info).__dict__,
		"turkiye_inventory": EsfaEyesProductInfo(who_can_see=users_with_international_sales_info).__dict__,
	}

def default_products_info():
	return {
		"unproduced_workshop_inventory": EsfaEyesProductInfo({
				"Esfa Meter": 0,
				"Pishtaz": 0,
				"Other": 0,
			},update_interval_days=7, who_can_see=users_with_products_info_access).__dict__,
		"ready_products": EsfaEyesProductInfo({
				"Esfa Meter": 0,
				"Pishtaz": 0,
				"Other": 0,
			},update_interval_days=7, who_can_see=users_with_products_info_access).__dict__,
	}

def default_kia_products_info():
	return {
		"unproduced_kia_workshop_inventory": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=7, who_can_see=users_with_kia_products_info_access).__dict__,
		"ready_kia_products": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=7, who_can_see=users_with_kia_products_info_access).__dict__,
		"deliverd_1404": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=7, who_can_see=users_with_kia_products_info_access).__dict__,
		"deliverd_1403": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=180, who_can_see=users_with_kia_products_info_access).__dict__,
		"deliverd_1402": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=180, who_can_see=users_with_kia_products_info_access).__dict__,
		"deliverd_1401": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=180, who_can_see=users_with_kia_products_info_access).__dict__,
		"deliverd_1400": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
				"Nira48-600": 0,
				"Nira110-600": 0,
			},update_interval_days=180, who_can_see=users_with_kia_products_info_access).__dict__,
		"deliverd_1399": EsfaEyesProductInfo({
						"121": 0,
						"131": 0,
						"Kia Meter": 0,
						"Nira48-600": 0,
						"Nira110-600": 0,
					},update_interval_days=180, who_can_see=users_with_kia_products_info_access).__dict__,
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
			},update_interval_days=7, who_can_see=users_with_kavosh_products_info_access).__dict__,
		"ready_kavosh_products": EsfaEyesProductInfo({
				"T22": 0,
				"TDM": 0,
				"TEM": 0,
				"CM1": 0,
				"CB1": 0,
				"CAPTAN12": 0,
				"MCM": 0,
			},update_interval_days=7, who_can_see=users_with_kavosh_products_info_access).__dict__,
	}


class EsfaEyes(models.Model):
	year = models.CharField("year", max_length=4, default="1404")
	financial_info = models.JSONField(default=default_financial_info)
	international_finance_info = models.JSONField(default=default_international_finance_info)
	international_sales_info = models.JSONField(default=default_international_sales_info)
	products_info = models.JSONField(default=default_products_info)
	kavosh_products_info = models.JSONField(default=default_kavosh_products_info)
	kia_products_info = models.JSONField(default=default_kia_products_info)

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

		return info

	def update_user_access(self):
		for field_name, users_list in access_mappings.items():
			field_data = getattr(self, field_name)
			if isinstance(field_data, dict):
				for key in field_data:
					if isinstance(field_data[key], dict):
						field_data[key]['who_can_see'] = users_list.copy()

				
				setattr(self, field_name, field_data)
