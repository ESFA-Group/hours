import jdatetime as jdt

class EsfaEyesInfo:
    def __init__(self, info={}, update_interval_days=2):
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
            }, update_interval_days=31):
        super().__init__(info, update_interval_days)

class EsfaEyesProductInfo(EsfaEyesInfo):
    def __init__(self, info={
                "Kavosh": 0,
                "Tan Module": 0,
                "Other Modules": 0,
                "MCM": 0,
                "Captan12": 0,
                "Esfa Meter": 0,
                "Kia Meter": 0,
                "Pishtaz": 0,
                "121": 0,
                "131": 0,
                "Other": 0,
            }, update_interval_days=31):
        super().__init__(info, update_interval_days)
