from django.urls import path
from . import views, api_views, login_views

app_name = 'sheets'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home_page'),

    path('signup', login_views.signup, name='signup'),
    path('login', login_views.login, name='login'),
    path('change_password', login_views.change_password, name='change_password'),
    path('logout', login_views.logout, name='logout'),

    path('hours', views.HoursView.as_view(), name='hours'),
    path('hours_info', views.HoursInfoView.as_view(), name='hours_info'),
    path('personal_info', views.PersonalInfoView.as_view(), name='personal_info'),
    path('payment', views.PaymentHandleView.as_view(), name='payment'),
    path('reports', views.ReportsView.as_view(), name='reports'),
    path('detailed_report', views.DetailedReportView.as_view(), name='detailed_report'),
    path('main_report', views.MainReportView.as_view(), name='main_report'),
    path('users_monthly_report', views.UsersMonthlyReportView.as_view(), name='users_monthly_report'),
    path('projects_yearly_report', views.ProjectsYearlyReportView.as_view(), name='projects_yearly_report'),
    path('payment_export', views.PaymentExportView.as_view(), name='payment_export'),
    path('hours_reports', views.HoursReportsView.as_view(), name='hours_reports'),

    path('api/info', api_views.InfoApiView.as_view(), name='api_info'),
    path('api/projects', api_views.ProjectListApiView.as_view(), name='api_projects'),
    path('api/sheets/<str:year>/<str:month>', api_views.SheetApiView.as_view(), name='api_sheets'),
    path('api/monthly_report/<str:year>/<str:month>', api_views.MonthlyReportApiView.as_view(), name='api_monthly_report'),
    path('api/yearly_report/<str:year>', api_views.YearlyReportApiView.as_view(), name='api_yearly_report'),
    path('api/payment/<str:year>/<str:month>', api_views.PaymentApiView.as_view(), name='api_payment'),
]