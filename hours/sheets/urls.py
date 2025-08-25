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
    path("daily_report", views.DailyReport.as_view(), name="daily_report"),
    path("daily_report_management", views.DailyReportManagement.as_view(), name="daily_report_management"),
    path("payment", views.PaymentHandleView.as_view(), name="payment"),
    path("order_food_form", views.FoodFormView.as_view(), name="food_form"),
    path("alter_food_data", views.FoodDataView.as_view(), name="food_data"),
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
        "api/FoodManagement/<str:year>/<str:month>",
        api_views.FoodManagementApiView.as_view(),
        name="api_FoodManagement",
    ),
    path(
        "api/food_cost_management/<str:year>/<str:month>",
        api_views.FoodCostManagementApiView.as_view(),
        name="api_FoodCostManagement",
    ),
    path(
        "api/FoodData/<str:year>/<str:month>",
        api_views.FoodDataApiView.as_view(),
        name="api_FoodData",
    ),
    path(
        "api/order_food/<str:year>/<str:month>",
        api_views.OrderFoodApiView.as_view(),
        name="api_order_food",
    ),
    path(
        "api/daily_foods_order/<str:year>/<str:month>/<str:weekIndex>/<str:day>",
        api_views.DailyFoodsOrder.as_view(),
        name="api_daily_foods_order",
    ),
    path(
        "api/daily_report_user/<str:year>/<str:month>/<str:day>",
        api_views.DailyReportUser.as_view(),
        name="api_daily_report_user",
    ),
    path(
        "api/daily_report_management/<str:year>/<str:month>",
        api_views.DailyReportManagement.as_view(),
        name="api_daily_report_management",
    ),
    path(
        "api/daily_report_setting_management",
        api_views.DailyReportSettingManager.as_view(),
        name="daily_report_setting_management",
    ),
]
