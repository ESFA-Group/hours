from django.db import models
from django.contrib.auth.models import AbstractUser

import pandas as pd
import jdatetime as jdt


def user_directory_path(instance, filename) -> str:
    # file will be uploaded to MEDIA_ROOT/personal/username/<filename>
    return f"personal/{instance.username}/{filename}"


class User(AbstractUser):
    # payment info
    wage = models.IntegerField("wage", default=0)
    base_payment = models.IntegerField("base_payment", default=0)
    reduction1 = models.IntegerField("reduction1", default=0)
    reduction2 = models.IntegerField("reduction2", default=0)
    reduction3 = models.IntegerField("reduction3", default=0)
    addition1 = models.IntegerField("addition", default=0)
    comment = models.TextField("comment", default="", blank=True)

    # personal info
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
            "addition1": self.addition1,
        }
        return info


def current_year() -> int:
    return jdt.date.today().year


def current_month() -> int:
    return jdt.date.today().month


def current_mont_days(month: int, isleap: bool) -> int:
    """gets a month and returns that date's month days number with leap year consideration
    (for jalali months)"""

    days_num = jdt.j_days_in_month[month - 1]
    if month == 12 and isleap:
        days_num += 1
    return days_num


class Sheet(models.Model):
    payment_status_choices = [
        (0, 'Not paid'),
        (1, 'Base paid'),
        (2, 'Completly paid'),
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
    mean = models.PositiveIntegerField("mean", default=0)  # in minutes
    total = models.PositiveIntegerField("total", default=0)  # in minutes
    submitted = models.BooleanField("submitted", default=False)
    payment_status = models.IntegerField("payment_status", choices=payment_status_choices, default=0)
    
    # payment info: data comes from user
    wage = models.IntegerField("wage", default=0)
    base_payment = models.IntegerField("base_payment", default=0)
    reduction1 = models.IntegerField("reduction1", default=0)
    reduction2 = models.IntegerField("reduction2", default=0)
    reduction3 = models.IntegerField("reduction3", default=0)
    addition1 = models.IntegerField("addition", default=0)

    def __str__(self):
        return f"{self.user_name}_{self.year}_{self.month}"

    def save(self, *args, **kwargs):
        if not len(self.data):
            today = jdt.date.today()
            month, year = today.month, today.year
            self.data = Sheet.empty_sheet_data(year, month)
        df = self.transform()
        self.mean = self.get_mean(df)
        self.total = self.get_total(df)
        super(Sheet, self).save(*args, **kwargs)

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

    def parse_project_porp(self, string: str) -> int:
        try:
            return int(string.replace("%", "").strip()) / 100
        except:
            return 0

    def get_sheet_projects(self, df: pd.DataFrame) -> list:
        defaults = ["Day", "WeekDay", "Hours"]
        projects = df.columns.difference(defaults)
        return list(projects)

    def transform(self) -> pd.DataFrame:
        """transforms sheet data to a pandas DataFrame.
        all project cols and "Hours" col will contain minutes instead of hh:mm and percentage format
        """
        df = pd.DataFrame(self.data)
        if "Hours" not in df.columns:
            return df
        projects = self.get_sheet_projects(df)
        df["Hours"] = df["Hours"].apply(self.hhmm2minutes)
        df[projects] = (
            df[projects]
            .applymap(self.parse_project_porp)
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
            - (self.reduction1 + self.reduction2 + self.reduction3)
            + self.addition1
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
            "addition1": self.addition1,
            "finalPayment": self.get_final_payment(),
            "complementaryPayment": self.get_complementary_payment(),
            "paymentStatus": self.payment_status,
        }
        return info

    def get_public_payment_info(self) -> dict:
        info = {
            "basePayment": self.get_base_payment(),
            "complementaryPayment": self.get_complementary_payment(),
            "paymentStatus": self.payment_status,
        }
        return info


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
        on_delete=models.CASCADE,
        null=True,
    )
    name = models.CharField("name", max_length=150)

    def __str__(self):
        return f"{self.family.name}-{self.name}"
