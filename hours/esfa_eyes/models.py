from django.db import models
from .schemas import esfa_eyes_info as schemas
from .schemas.esfa_eyes_info import EsfaEyesInfo, EsfaEyesMonltyInfo, EsfaEyesProductInfo
from sheets.models import User

def default_financial_info():
	return {
		'balance_rials_official': EsfaEyesInfo(0).__dict__,
		'balance_rials': EsfaEyesInfo(0).__dict__,
		'montly_checks_recieved': EsfaEyesMonltyInfo().__dict__,
		'montly_checks_issued': EsfaEyesMonltyInfo().__dict__,
		'montly_installment': EsfaEyesMonltyInfo().__dict__,
		'montly_total_sales': EsfaEyesMonltyInfo().__dict__,
		'individual_sales': EsfaEyesProductInfo().__dict__,
		'total_insured_staffs': EsfaEyesInfo(0).__dict__,
		'total_uninsured_staffs': EsfaEyesInfo(0).__dict__,
		'total_salary_paid': EsfaEyesInfo(0).__dict__,
		'total_insurance_paid': EsfaEyesInfo(0).__dict__,
	}

def default_international_finance_info():
	return {
		"balance_dollars": EsfaEyesInfo(0).__dict__,
		"china_production_orders": EsfaEyesProductInfo().__dict__,
	}

def default_international_sales_info():
	return {
		"montly_international_total_sales": EsfaEyesMonltyInfo().__dict__,
		"international_individual_sales": EsfaEyesProductInfo().__dict__,
		"turkiye_inventory": EsfaEyesProductInfo().__dict__,
	}

def default_products_info():
	return {
		"unproduced_workshop_inventory": EsfaEyesProductInfo().__dict__,
		"ready_products": EsfaEyesProductInfo().__dict__,
	}


class EsfaEyes(models.Model):
	year = models.CharField("year", max_length=4, default="1404")
	financial_info = models.JSONField(default=default_financial_info)
	international_finance_info = models.JSONField(default=default_international_finance_info)
	international_sales_info = models.JSONField(default=default_international_sales_info)
	products_info = models.JSONField(default=default_products_info)

	def __str__(self):
		return f"ESFA Eyes - {self.year}"

	def get(self, user: User):
		info = {}
		if user:
			if user.is_FinancialManager:
				info.update(self.financial_info)
			if user.is_InternationalFinanceManager:
				info.update(self.international_finance_info)
			if user.is_InternationalSalesManager:
				info.update(self.international_sales_info)
			if user.is_ProductionManager:
				info.update(self.products_info)
		return info
	
	def update(self, newData, field_name):
		print(self.international_finance_info)
		for fields in newData:
			print(fields) 
		info = {}
 