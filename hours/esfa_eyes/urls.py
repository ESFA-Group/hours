# new_app/urls.py
from django.urls import path
from django.views.generic.base import RedirectView
from . import views, api_views

app_name = "esfa_eyes"

urlpatterns = [
    # views
    path("esfa_eyes_dashbord", views.EyesView.as_view(), name="Esfa Eyes Dashbord"),
    # apis
    path("api/eyes/<str:year>", api_views.EsfaEyesApiView.as_view(), name="api_eyes",)
]