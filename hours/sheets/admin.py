from django.contrib import admin
from django.contrib.auth.models import Group
from sheets.models import *

admin.site.site_url = "/hours"

admin.site.unregister(Group)

admin.site.register(ProjectFamily)
admin.site.register(Sheet)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ordering = ["last_name", "first_name"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    ordering = ["family__name"]
