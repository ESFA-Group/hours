from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import QuerySet, Sum

import jdatetime as jdt
import pandas as pd
import re

from sheets.models import Project, Sheet, User
from sheets.serializers import ProjectSerializer, SheetSerializer


def camel_to_snake(s: str) -> str:
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    snake = pattern.sub("_", s).lower()
    return snake


def _setup_sheet(sheet, user):
    sheet.user_name = user.get_full_name()
    sheet.wage = user.wage
    sheet.base_payment = user.base_payment
    sheet.reduction1 = user.reduction1
    sheet.reduction2 = user.reduction2
    sheet.reduction3 = user.reduction3
    sheet.addition1 = user.addition1
    return sheet


class ProjectListApiView(ListAPIView):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]


class SheetApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, year: str, month: str):
        try:
            sheet = Sheet.objects.get(user=self.request.user, year=year, month=month)
        except Sheet.DoesNotExist:
            empty_sheet_data = Sheet.empty_sheet_data(int(year), int(month))
            res = {
                "data": empty_sheet_data,
                "month": month,
                "year": year,
                "submitted": False,
            }
            return Response(res, status=status.HTTP_200_OK)

        serializer = SheetSerializer(sheet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, year: str, month: str):
        if "saveSheet" in request.data:
            user = self.request.user
            sheet, created = Sheet.objects.get_or_create(
                user=user, year=year, month=month
            )
            sheet.user_name = user.get_full_name()
            sheet.wage = user.wage
            sheet.base_payment = user.base_payment
            sheet.reduction1 = user.reduction1
            sheet.reduction2 = user.reduction2
            sheet.reduction3 = user.reduction3
            sheet.addition1 = user.addition1
            data = request.data.get("data", [])
            data.sort(key=lambda row: int(row.get("Day", 0)))
            sheet.data = request.data["data"]
            sheet.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        elif "editSheet" in request.data:
            data = request.data.get("row", {})
            field = request.data.get("field", "")
            user = User.objects.get(pk=data["userID"])
            update_data = {camel_to_snake(field): data[field]}
            sheet = Sheet.objects.filter(user=user, year=year, month=month)
            sheet.update(**update_data)
            return Response(sheet.first().get_payment_info(), status=status.HTTP_200_OK)

    def put(self, request, year: str, month: str):
        try:
            sheet = Sheet.objects.get(user=self.request.user, year=year, month=month)
        except Sheet.DoesNotExist:
            return Response({"notFound": True}, status=status.HTTP_404_NOT_FOUND)
        if (
            request.user.check_info()
        ):  # if the user has entered needed personal information
            sheet.submitted = True
            sheet.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response({"flaw": True}, status=status.HTTP_200_OK)


class InfoApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        today = jdt.date.today()
        month, year = today.month, today.year

        all_sheets = Sheet.objects.all()

        user_month_info = self.get_info(
            all_sheets.filter(user=request.user, month=month)
        )
        user_year_info = self.get_info(
            all_sheets.filter(user=request.user, year=year).exclude(month=month)
        )
        user_year_info = user_year_info.add(user_month_info, fill_value=0)
        user_tot_info = self.get_info(
            all_sheets.filter(user=request.user).exclude(year=year)
        )
        user_tot_info = user_tot_info.add(user_year_info, fill_value=0)

        esfa_month_info = self.get_info(all_sheets.filter(month=month))
        esfa_year_info = self.get_info(
            all_sheets.filter(year=year).exclude(month=month)
        )
        esfa_year_info = esfa_year_info.add(esfa_month_info, fill_value=0)
        esfa_tot_info = self.get_info(all_sheets.exclude(year=year))
        esfa_tot_info = esfa_tot_info.add(esfa_year_info, fill_value=0)

        last_month = month - 1 if month != 1 else 12
        monthly_sheets = (
            Sheet.objects.filter(year=year, user=request.user)
            .values("total", "month")
            .order_by("month")
        )
        user_monthly_hours = list(monthly_sheets)
        info = {
            "user_month_info": user_month_info.to_dict(),
            "user_year_info": user_year_info.to_dict(),
            "user_tot_info": user_tot_info.to_dict(),
            "esfa_month_info": esfa_month_info.to_dict(),
            "esfa_year_info": esfa_year_info.to_dict(),
            "esfa_tot_info": esfa_tot_info.to_dict(),
            "last_hero": self.get_hero(year, last_month),
            "last_esfa_mean": self.get_month_mean(year, last_month),
            "last_user_mean": self.get_month_mean(year, last_month, user=request.user),
            "user_monthly_hours": user_monthly_hours,
        }

        # print('info is:', info)
        return Response(info, status=status.HTTP_200_OK)

    def get_hero(self, year: int, month: int) -> str:
        hero_name = "Anonymous Anonymousian"
        hero = Sheet.objects.filter(year=year, month=month).order_by("-total").first()
        if hero:  # hero may be None
            hero_name = hero.user.get_full_name()
        return hero_name

    def get_month_mean(self, year: int, month: int, user=None) -> str:
        sheets = Sheet.objects.filter(year=year, month=month)
        if user is not None:
            sheets = sheets.filter(user=user)
        if not sheets.count():
            return 0
        tot = sheets.aggregate(Sum("total"))
        return tot["total__sum"] / sheets.count()

    def get_info(self, queryset: QuerySet) -> pd.Series:
        if not queryset.count():
            return pd.Series(dtype="float64")
        df_all = pd.DataFrame()
        for sheet in queryset:
            df = sheet.transform()
            df.drop(["Day", "WeekDay"], axis=1, inplace=True)
            df_all = df_all.add(df, fill_value=0)
        return df_all.sum()


class PublicMonthlyReportApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, year: str, month: str):

        sheets = Sheet.objects.filter(year=year, month=month)
        hours, activeUsers = PublicMonthlyReportApiView.get_sheet_sums(sheets)
        res = {
            "hours": hours,
            "activeUsers": activeUsers,
        }

        return Response(res, status=status.HTTP_200_OK)

    @classmethod
    def get_sheet_sums(cls, sheets: QuerySet) -> dict:
        projects = [p["name"] for p in Project.objects.values("name")]
        projects.append("Total")

        # a pandas Series which will be a summation of all desiered sheet sums
        projects_sum = pd.Series({p: 0 for p in projects})

        for sheet in sheets:
            sheet_sum = cls.get_sum(sheet)
            projects_sum = projects_sum.add(sheet_sum, fill_value=0)

        return projects_sum.apply(cls.minute_formatter).to_dict(), sheets.count()

    @classmethod
    def get_sum(self, sheet: Sheet) -> pd.Series:
        """returns sheet column sums"""
        df = sheet.transform()
        df.drop(["Day", "WeekDay"], axis=1, inplace=True)
        df.rename(columns={"Hours": "Total"}, inplace=True)
        return df.sum()

    @classmethod
    def minute_formatter(cls, minutes: int) -> str:
        return f"{int(minutes // 60)}:{int(minutes % 60)}"


class MonthlyReportApiView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, year: str, month: str):

        sheets = Sheet.objects.filter(year=year, month=month)
        submitted_sheets = sheets.filter(submitted=True)
        submitted_user_names = [
            sheet.user.get_full_name() for sheet in submitted_sheets
        ]
        sheetless_users = User.objects.select_related().exclude(
            sheets__year=year, sheets__month=month
        )
        sheetless_user_names = [user.get_full_name() for user in sheetless_users]
        hours, payments = MonthlyReportApiView.get_sheet_sums(sheets, sheetless_users)
        res = {
            "hours": hours,
            # "payments": payments,
            "usersNum": User.objects.count(),
            "sheetsNum": sheets.count(),
            "submittedSheetsNum": submitted_sheets.count(),
            "sheetlessUsers": sheetless_user_names,
            "submittedUsers": submitted_user_names,
        }

        return Response(res, status=status.HTTP_200_OK)

    @classmethod
    def get_sheet_sums(cls, sheets: QuerySet, sheetless_users: QuerySet) -> dict:
        projects = [p["name"] for p in Project.objects.values("name")]
        projects.append("Total")

        # a pandas Series which contains all projects.
        # a user's sheet sum should be added to this Series in order to contain all projects even the value is 0
        projects_empty = pd.Series({p: 0 for p in projects})
        # a pandas Series which will be a summation of all desiered sheet sums
        projects_sum = pd.Series({p: 0 for p in projects})

        hours = dict()
        payments = dict()
        for sheet in sheets:
            sheet_sum = cls.get_sum(sheet)
            sheet_sum = projects_empty.add(sheet_sum, fill_value=0)
            projects_sum = projects_sum.add(sheet_sum, fill_value=0)
            full_name = sheet.user.get_full_name()
            hours[full_name] = sheet_sum.apply(cls.minute_formatter).to_dict()
            wage = sheet.user.wage
            payments[full_name] = sheet_sum.apply(
                lambda x: int(x / 60 * wage)
            ).to_dict()
        for user in sheetless_users:
            full_name = user.get_full_name()
            hours[full_name] = projects_empty.to_dict()
            payments[full_name] = 0
        hours["Total"] = projects_sum.apply(cls.minute_formatter).to_dict()
        return hours, payments

    @classmethod
    def get_sum(self, sheet: Sheet) -> pd.Series:
        """returns sheet column sums"""
        df = sheet.transform()
        df.drop(["Day", "WeekDay"], axis=1, inplace=True)
        df.rename(columns={"Hours": "Total"}, inplace=True)
        return df.sum()

    @classmethod
    def minute_formatter(cls, minutes: int) -> str:
        return f"{int(minutes // 60)}:{int(minutes % 60)}"


class PaymentApiView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, year: str, month: str):
        sheets = (
            Sheet.objects.select_related("user")
            .filter(year=year, month=month)
            .order_by("user__last_name")
        )
        data = list()
        for sheet in sheets:
            user = sheet.user
            if not sheet.user:
                continue
            payment_info = sheet.get_payment_info()
            payment_info.update(
                {
                    "userID": user.id,
                    "user": user.get_full_name() + (" ☑️" if sheet.submitted else ""),
                    "bankName": user.bank_name,
                }
            )
            data.append(payment_info)

        return Response(data, status=status.HTTP_200_OK)


class PublicPaymentApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, year: str, month: str):
        sheet = Sheet.objects.get(user=self.request.user, year=year, month=month)
        data = sheet.get_public_payment_info()
        return Response(data, status=status.HTTP_200_OK)


class AlterPaymentApiView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, year: str, month: str):
        users = User.objects.all()
        data = list()

        for user in users:
            sheet, created = Sheet.objects.get_or_create(
                user=user, year=year, month=month
            )
            if created:
                sheet = _setup_sheet(sheet, user)
                sheet.save()
            payment_info = sheet.get_payment_info()
            payment_info.update(
                {
                    "userID": user.id,
                    "user": user.get_full_name(),
                    "bankName": user.bank_name,
                }
            )
            data.append(payment_info)

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, year: str, month: str):
        editted_row = request.data["row"]
        id = editted_row["userID"]
        wage = editted_row["wage"]
        base = editted_row["basePayment"]

        user = User.objects.get(pk=id)
        user.wage = wage
        user.base_payment = base
        user.save()
        user_sheets = Sheet.objects.filter(user=id, year=1403)
        for sheet in user_sheets:
            if sheet.month >= int(month):
                sheet.wage = wage
                sheet.base_payment = base
                sheet.save()

        currentSheet = Sheet.objects.get(user=id, year=1403, month=month)
        currentSheet.reduction1 = int(editted_row["reduction1"])
        currentSheet.reduction2 = int(editted_row["reduction2"])
        currentSheet.reduction3 = int(editted_row["reduction3"])
        currentSheet.addition1 = int(editted_row["addition1"])
        currentSheet.payment_status = int(editted_row["paymentStatus"])
        currentSheet.save()

        return Response(currentSheet.get_payment_info(), status=status.HTTP_200_OK)
