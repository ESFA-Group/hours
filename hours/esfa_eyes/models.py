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
		"unproduced_workshop_inventory": EsfaEyesProductInfo(update_interval_days=7).__dict__,
		"ready_products": EsfaEyesProductInfo(update_interval_days=7).__dict__,
	}


class EsfaEyes(models.Model):
	year = models.CharField("year", max_length=4, default="1404")
	financial_info = models.JSONField(default=default_financial_info)
	international_finance_info = models.JSONField(default=default_international_finance_info)
	international_sales_info = models.JSONField(default=default_international_sales_info)
	products_info = models.JSONField(default=default_products_info)

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
			return info
		if user.is_FinancialManager:
			info.update(self.financial_info)
		if user.is_InternationalFinanceManager:
			info.update(self.international_finance_info)
		if user.is_InternationalSalesManager:
			info.update(self.international_sales_info)

		obj = self._get_production_info(user)
		info.update(obj)
		return info 

	def _get_production_info(self, user: User):
		if not user:
			return {}
		
		if user.is_ProductionManagerReadonly or (user.is_ProductionManager and user.is_R131ProductionManager):
			return copy.deepcopy(self.products_info)

		valid_production_info = copy.deepcopy(self.products_info)
		rp = valid_production_info["ready_products"]["_info"]
		selected_keys = ["121", "Kia Meter", "131"]
		
		if user.is_ProductionManager:
			valid_rp_info = {k: v for k, v in rp.items() if k not in selected_keys}
			valid_production_info["ready_products"]["_info"] = valid_rp_info
   
		if user.is_R131ProductionManager:
			valid_rp_info = {key: rp[key] for key in selected_keys if key in rp}
			valid_production_info["ready_products"]["_info"] = valid_rp_info

		return valid_production_info
