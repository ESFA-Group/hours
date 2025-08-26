from django.db import models
from functools import partial
from schemas.esfa_eyes_info import *

    
class EsfaEyes(models.Model):
    year = models.CharField('year', max_length=4, default='1404')
    financial_info = models.JSONField(default=partial(dict, 
        {
            'balance_rials_official': EsfaEyesInfo(0),
            'balance_rials': EsfaEyesInfo(0),
            'montly_checks_recieved': EsfaEyesMonltyInfo(),
            'montly_checks_issued': EsfaEyesMonltyInfo(),
            'montly_installment ': EsfaEyesMonltyInfo(),
            'montly_total_sales': EsfaEyesMonltyInfo(),
            'individual_sales': EsfaEyesProductInfo(),
            'total_insured_staffs': EsfaEyesInfo(0),
            'total_uninsured_staffs': EsfaEyesInfo(0),
            'total_salary_paid': EsfaEyesInfo(0),
            'total_insurance_paid': EsfaEyesInfo(0),
        }
    ))
    international_finance_info = models.JSONField(default=partial(dict, 
        {
            'balance_dollars': EsfaEyesInfo({}),
            'china_production_orders': EsfaEyesProductInfo(),
        }
    ))
    international_sales_info = models.JSONField(default=partial(dict, 
        {
            'montly_international_total_sales': EsfaEyesMonltyInfo(),
            'international_individual_sales': EsfaEyesProductInfo(),
            'china_production_orders': EsfaEyesProductInfo(),
        }
    ))
    products_info = models.JSONField(default=partial(dict, 
        {
            'unproduced_workshop_inventory': EsfaEyesProductInfo(),
            'ready_products': EsfaEyesProductInfo(),
        }
    ))


    def get(self, info=None):
        """Return a DateInfo instance.

        If `info` is omitted, a combined dict of the model's financial
        fields is used as the payload.
        """
        if info is None:
            info = {
                'financial_info': self.financial_info,
                'international_finance_info': self.international_finance_info,
            }
        return self.DateInfo(info)
