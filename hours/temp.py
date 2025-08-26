import jdatetime as jdt
import time
from typing import TypedDict

class EsfaEyesInfo:
    def __init__(self, info={}, update_interval_days=1):
        self.UPDATE_INTERVAL_DAYS =  update_interval_days
        self.last_modify_time = jdt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._info = info if info is not None else {}
    
    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, value={}):
        self._info = value if value is not None else {}
        self.last_modify_time = jdt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class EsfaEyesMonltyInfo(EsfaEyesInfo):
    def __init__(self, info={
                "فرردین": 0,
                "اردیبهشت": 0,
                "خرداد": 0,
                "تیر": 0,
                "مرداد": 0,
                "شهریور": 0,
                "مهر": 0,
                "ابان": 0,
                "اذر": 0,
                "دی": 0,
                "بهمن": 0,
                "اسفند": 0,
            }, update_interval_days=1):
        super().__init__(info, update_interval_days)

class EsfaEyesProductInfo(EsfaEyesInfo):
    def __init__(self, info={
                "kavosh": 0,
                "tan_module": 0,
                "other_modules": 0,
                "mcm": 0,
                "captan12": 0,
                "esfa_meter": 0,
                "kia_meter": 0,
                "pishtaz": 0,
                "121": 0,
                "131": 0,
                "software": 0,
            }, update_interval_days=1):
        super().__init__(info, update_interval_days)

		
    
a = {"data": EsfaEyesProductInfo()}

print(a["data"].last_modify_time, a["data"].info, a["data"].UPDATE_INTERVAL_DAYS)