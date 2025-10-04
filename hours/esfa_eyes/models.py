from django.db import models
from .schemas import esfa_eyes_info as schemas
from .schemas.esfa_eyes_info import EsfaEyesInfo, EsfaEyesMonltyInfo, EsfaEyesProductInfo
from sheets.models import User
import copy

def default_financial_info():
	return {
		'balance_rials_official': EsfaEyesInfo(0).__dict__,
		'balance_rials': EsfaEyesInfo(0).__dict__,
		'montly_checks_received': EsfaEyesMonltyInfo().__dict__,
		'montly_checks_issued': EsfaEyesMonltyInfo().__dict__,
		'montly_installment': EsfaEyesMonltyInfo().__dict__,
		'montly_total_sales': EsfaEyesMonltyInfo(update_interval_days=14).__dict__,
		'individual_sales': EsfaEyesProductInfo().__dict__,
		'individual_sales_quantities': EsfaEyesProductInfo().__dict__,
		'individual_sales_total_received': EsfaEyesProductInfo().__dict__,
		'individual_sales_check_received': EsfaEyesProductInfo().__dict__,
		'individual_sales_unknown': EsfaEyesProductInfo().__dict__,
		'total_insured_staffs': EsfaEyesInfo(0, 31).__dict__,
		'total_uninsured_staffs': EsfaEyesInfo(0, 31).__dict__,
		'total_salary_paid': EsfaEyesMonltyInfo().__dict__,
		'total_insurance_paid': EsfaEyesMonltyInfo().__dict__,
	}

def default_international_finance_info():
	return {
		"balance_dollars": EsfaEyesProductInfo({
                "مقدار 1": 0,
                "مقدار 2": 0,
                "مقدار 3": 0,
                "مقدار 4": 0,
                "مقدار 5": 0,
                "مقدار کل": 0,
            }, 2).__dict__,
		"china_production_orders": EsfaEyesProductInfo().__dict__,
	}

def default_international_sales_info():
	return {
		"montly_international_total_sales": EsfaEyesMonltyInfo(update_interval_days=14).__dict__,
		# "international_individual_sales": EsfaEyesProductInfo().__dict__,
		# "international_individual_sales_quantities": EsfaEyesProductInfo().__dict__,
		"turkiye_inventory": EsfaEyesProductInfo().__dict__,
	}

def default_products_info():
	return {
		"unproduced_workshop_inventory": EsfaEyesProductInfo({
				"Esfa Meter": 0,
				"Pishtaz": 0,
				"Other": 0,
			},update_interval_days=7).__dict__,
		"ready_products": EsfaEyesProductInfo({
				"Esfa Meter": 0,
				"Pishtaz": 0,
				"Other": 0,
			},update_interval_days=7).__dict__,
	}

def default_kia_products_info():
	return {
		"unproduced_kia_workshop_inventory": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
                "Nira48-600": 0,
                "Nira110-600": 0,
			},update_interval_days=7).__dict__,
		"ready_kia_products": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
                "Nira48-600": 0,
                "Nira110-600": 0,
			},update_interval_days=7).__dict__,
		"deliverd_1404": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
                "Nira48-600": 0,
                "Nira110-600": 0,
			},update_interval_days=7).__dict__,
		"deliverd_1403": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
                "Nira48-600": 0,
                "Nira110-600": 0,
			},update_interval_days=180).__dict__,
		"deliverd_1402": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
                "Nira48-600": 0,
                "Nira110-600": 0,
			},update_interval_days=180).__dict__,
		"deliverd_1401": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
                "Nira48-600": 0,
                "Nira110-600": 0,
			},update_interval_days=180).__dict__,
		"deliverd_1400": EsfaEyesProductInfo({
				"121": 0,
				"131": 0,
				"Kia Meter": 0,
                "Nira48-600": 0,
                "Nira110-600": 0,
			},update_interval_days=180).__dict__,
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
			},update_interval_days=7).__dict__,
		"ready_kavosh_products": EsfaEyesProductInfo({
				"T22": 0,
				"TDM": 0,
				"TEM": 0,
				"CM1": 0,
				"CB1": 0,
				"CAPTAN12": 0,
				"MCM": 0,
			},update_interval_days=7).__dict__,
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
		if user.is_FinancialManager:
			info.update(self.financial_info)
		if user.is_InternationalFinanceManager:
			info.update(self.international_finance_info)
		if user.is_InternationalSalesManager:
			info.update(self.international_sales_info)
		if user.is_ProductionManager:
			info.update(self.products_info)
		if user.is_KavoshProductionManager:
			info.update(self.kavosh_products_info)
		if user.is_KiaProductionManager:
			info.update(self.kia_products_info)

		return info
