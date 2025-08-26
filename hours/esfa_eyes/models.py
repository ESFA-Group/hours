from django.db import models
from .schemas import esfa_eyes_info as schemas
from .schemas.esfa_eyes_info import EsfaEyesInfo, EsfaEyesMonltyInfo, EsfaEyesProductInfo
from sheets.models import User

def default_financial_info():
    return {
        'balance_rials_official': EsfaEyesInfo(0),
        'balance_rials': EsfaEyesInfo(0),
        'montly_checks_recieved': EsfaEyesMonltyInfo(),
        'montly_installment': EsfaEyesMonltyInfo(),
        'montly_total_sales': EsfaEyesMonltyInfo(),
        'individual_sales': EsfaEyesProductInfo(),
        'total_insured_staffs': EsfaEyesInfo(0),
        'total_uninsured_staffs': EsfaEyesInfo(0),
        'total_salary_paid': EsfaEyesInfo(0),
        'total_insurance_paid': EsfaEyesInfo(0),
    }


def default_international_finance_info():
    return {
        "balance_dollars": {},
        "china_production_orders": EsfaEyesProductInfo(),
    }


def default_international_sales_info():
    return {
        "montly_international_total_sales": EsfaEyesMonltyInfo(),
        "international_individual_sales": EsfaEyesProductInfo(),
        "china_production_orders": EsfaEyesProductInfo(),
    }


def default_products_info():
    return {
        "unproduced_workshop_inventory": EsfaEyesProductInfo(),
        "ready_products": EsfaEyesProductInfo(),
    }


class EsfaEyes(models.Model):
    year = models.CharField("year", max_length=4, default="1404")
    financial_info = models.JSONField(default=default_financial_info)
    international_finance_info = models.JSONField(default=default_international_finance_info)
    international_sales_info = models.JSONField(default=default_international_sales_info)
    products_info = models.JSONField(default=default_products_info)

    def get(self, user: User):
        if user:
            if user.is_FinancialManager:
                info = self.financial_info
            elif user.is_InternationalFinanceManager:
                info = self.international_finance_info
            elif user.is_InternationalSalesManager:
                info = self.international_sales_info
            elif user.is_ProductionManager:
                info = self.products_info
            return info
        return {}	
