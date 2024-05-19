from django.urls import path
from django.views.generic.base import RedirectView
from . import views, api_views, login_views

app_name = "sheets"

urlpatterns = [
    path("", RedirectView.as_view(url="home", permanent=True)),
    path("home", views.HomePageView.as_view(), name="home_page"),
    path("signup", login_views.signup, name="signup"),
    path("login", login_views.login, name="login"),
    path("change_password", login_views.change_password, name="change_password"),
    path("logout", login_views.logout, name="logout"),
    path("hours", views.HoursView.as_view(), name="hours"),
    path("hours_info", views.HoursInfoView.as_view(), name="hours_info"),
    path("personal_info", views.PersonalInfoView.as_view(), name="personal_info"),
    path("payment", views.PaymentHandleView.as_view(), name="payment"),
    path("alter_payment", views.AlterPaymentHandleView.as_view(), name="alter_payment"),
    path("reports", views.ReportsView.as_view(), name="reports"),
    path("detailed_report", views.DetailedReportView.as_view(), name="detailed_report"),
    path("main_report", views.MainReportView.as_view(), name="main_report"),
    path(
        "users_monthly_report",
        views.UsersMonthlyReportView.as_view(),
        name="users_monthly_report",
    ),
    path(
        "projects_yearly_report",
        views.ProjectsYearlyReportView.as_view(),
        name="projects_yearly_report",
    ),
    path("payment_export", views.PaymentExportView.as_view(), name="payment_export"),
    path(
        "payment_excel_export/<str:year>/<str:month>",
        views.PaymentExcelExportView.as_view(),
        name="payment_excel_export",
    ),
    path(
        "payment_excel_import/<str:year>/<str:month>",
        views.PaymentExcelImportView.as_view(),
        name="payment_excel_import",
    ),
    path("api/info", api_views.InfoApiView.as_view(), name="api_info"),
    path("api/projects", api_views.ProjectListApiView.as_view(), name="api_projects"),
    path(
        "api/sheets/<str:year>/<str:month>",
        api_views.SheetApiView.as_view(),
        name="api_sheets",
    ),
    path(
        "api/public_monthly_report/<str:year>/<str:month>",
        api_views.PublicMonthlyReportApiView.as_view(),
        name="api_public_monthly_report",
    ),
    path(
        "api/monthly_report/<str:year>/<str:month>",
        api_views.MonthlyReportApiView.as_view(),
        name="api_monthly_report",
    ),
    path(
        "api/payment/<str:year>/<str:month>",
        api_views.PaymentApiView.as_view(),
        name="api_payment",
    ),
    path(
        "api/public_payment/<str:year>/<str:month>",
        api_views.PublicPaymentApiView.as_view(),
        name="api_public_payment",
    ),
    path(
        "api/alter_payment/<str:year>/<str:month>",
        api_views.AlterPaymentApiView.as_view(),
        name="api_alter_payment",
    ),
]
