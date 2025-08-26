from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.conf import settings

urlpatterns = [
    path("hours/admin/", admin.site.urls),
    path("hours/api-auth/", include("rest_framework.urls")),
    path("hours/", include("sheets.urls")),
    path("hours/", include("esfa_eyes.urls")),
    path("", RedirectView.as_view(url="hours", permanent=True)),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
