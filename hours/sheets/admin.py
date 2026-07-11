from django.contrib import admin
from django.contrib.auth.models import Group
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin
from sheets.models import *

admin.site.site_url = "/hours"


admin.site.register(ProjectFamily)

@admin.register(Sheet)
class SheetAdmin(admin.ModelAdmin):
    ordering = ["-year", "-month", "user_name"]
    list_filter = ['year', 'month', 'user_name', 'submitted', 'manager_level_1_verified', 'manager_level_2_verified', 'supreme_verified']
    search_fields = ['user_name', 'user__first_name_p', 'user__last_name_p', 'user__username'] 
    list_display = [
        'user_name',
        'month',
        'year',
        'submitted',
        'manager_level_1_verified',
        'manager_level_2_verified',
        'supreme_verified',
    ]


class UserResource(resources.ModelResource):
    manager_level_1 = fields.Field(
        column_name='manager_level_1',
        attribute='manager_level_1',
        widget=ForeignKeyWidget(User, 'username'),
    )
    manager_level_2 = fields.Field(
        column_name='manager_level_2',
        attribute='manager_level_2',
        widget=ForeignKeyWidget(User, 'username'),
    )

    class Meta:
        model = User
        # Explicitly exclude 'id' from import/export
        exclude = ('id',)
        fields = (
            'username',
            'first_name_p',
            'last_name_p',
            'staff_group_tag',
            'verifier_group_tags',
            'auto_hour_ID',
            'manager_level_1',
            'manager_level_2',
            'payment_type',
            'remote_percentage',
        )
        export_order = (
            'username',
            'first_name_p',
            'last_name_p',
            'staff_group_tag',
            'verifier_group_tags',
            'auto_hour_ID',
            'manager_level_1',
            'manager_level_2',
            'payment_type',
            'remote_percentage',
        )
        import_id_fields = ('username',)

    def before_import_row(self, row, **kwargs):
        for field_name in ('manager_level_1', 'manager_level_2'):
            username = str(row.get(field_name) or '').strip()
            if username and not User.objects.filter(username=username).exists():
                raise ValueError(f"{field_name}: username '{username}' does not exist")

        payment_type = str(row.get('payment_type') or '').strip()
        if payment_type and payment_type not in dict(User.payment_type_choices):
            allowed = ', '.join(dict(User.payment_type_choices).keys())
            raise ValueError(f"payment_type '{payment_type}' is invalid. Allowed values: {allowed}")


@admin.register(User)
class UserAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    # Your existing configurations
    ordering = ["last_name", "first_name"]
    filter_horizontal = ('groups', 'user_permissions')
    search_fields = ['last_name', 'first_name', 'username', 'first_name_p', 'last_name_p']
    autocomplete_fields = ['manager_level_1', 'manager_level_2']
    
    # Add these for better import/export experience
    list_display = ('username', 'last_name_p', 'first_name_p', 'staff_group_tag', 'manager_level_1', 'manager_level_2', 'payment_type')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'payment_type')
    
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
    
    def changelist_view(self, request, extra_context=None):
        if "is_active__exact" not in request.GET:
            q = request.GET.copy()
            q["is_active__exact"] = "1"
            request.GET = q
            request.META["QUERY_STRING"] = request.GET.urlencode()

        return super().changelist_view(request, extra_context)


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
