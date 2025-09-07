from django.contrib import admin
from django.contrib.auth.models import Group
from sheets.models import *

admin.site.site_url = "/hours"


admin.site.register(ProjectFamily)

@admin.register(Sheet)
class SheetAdmin(admin.ModelAdmin):
    ordering = ["-year", "-month", "user_name"]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ordering = ["last_name", "first_name"]
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    ordering = ["family__name"]

@admin.register(Food_data)
class Food_dataAdmin(admin.ModelAdmin):
    ordering = ["-year", "-month"]

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    ordering = ["year", "month", "day"]

@admin.register(DailyReportSetting)
class ReportSettingAdmin(admin.ModelAdmin):
    ordering = []
