# new_app/urls.py
from django.urls import path
from django.views.generic.base import RedirectView
from . import views, api_views

app_name = "esfa_eyes"

urlpatterns = [
    # views
    path("esfa_eyes_dashbord", views.EyesView.as_view(), name="Esfa Eyes Dashbord"),
    # apis
    path("api/eyes/<str:year>", api_views.EsfaEyesApiView.as_view(), name="api_eyes",),
    path("api/global_sales", api_views.GlobalSalesApiView.as_view(), name="global_sales",),
    path("api/detailed_sales", api_views.DetailedSalesApiView.as_view(), name="detailed_sales",),
    path("api/staff_info", api_views.StaffInfoApiView.as_view(), name="staff_info",)
]