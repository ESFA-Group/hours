from django.contrib import admin
from django.contrib.auth.models import Group
from import_export import resources, fields
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin
from sheets.models import *

admin.site.site_url = "/hours"


admin.site.register(ProjectFamily)

@admin.register(Sheet)
class SheetAdmin(admin.ModelAdmin):
    ordering = ["-year", "-month", "user_name"]
    list_filter = ['year', 'month', 'user_name']
    search_fields = ['user_name', 'user__first_name_p', 'user__last_name_p'] 
    list_display = ['user_name', 'month', 'year']


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        # Explicitly exclude 'id' from import/export
        exclude = ('id',)
        fields = ('username', 'first_name_p', 'last_name_p', 'staff_group_tag')
        export_order = ('username', 'first_name_p', 'last_name_p', 'staff_group_tag')
        import_id_fields = ('username',)


@admin.register(User)
class UserAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    # Your existing configurations
    ordering = ["last_name", "first_name"]
    filter_horizontal = ('groups', 'user_permissions')
    search_fields = ['last_name', 'first_name', 'username', 'first_name_p', 'last_name_p']
    
    # Add these for better import/export experience
    list_display = ('username', 'last_name_p', 'first_name_p', 'staff_group_tag')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    # Import-export resource
    resource_class = UserResource
    
    # Your existing restricted fields
    RESTRICTED_FIELDS = [
        'is_superuser',
        'is_staff',
        'is_ProjectReportManager',
        'is_SubReportManager',
        'is_MainReportManager',
        'is_FoodManager',
        'is_FinancialManager',
        'is_InternationalFinanceManager',
        'is_InternationalSalesManager',
        'is_ProductionManager',
        'is_KavoshProductionManager',
        'is_KiaProductionManager',
        'is_PaymentManager',
        'user_permissions',
        'groups'
    ]
    
    def get_exclude(self, request, obj=None):
        exclude = super().get_exclude(request, obj) or []
        
        if not request.user.is_superuser:
            return exclude + self.RESTRICTED_FIELDS
        return exclude


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
