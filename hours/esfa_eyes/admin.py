from django.contrib import admin
from esfa_eyes.models import EsfaEyes

# Register your models here.
@admin.register(EsfaEyes)
class EsfaEyesAdmin(admin.ModelAdmin):
    ordering = ["-year"]
