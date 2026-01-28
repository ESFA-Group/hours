from rest_framework import permissions


class hasEsfaEyesAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_superuser or request.user.is_FinancialManager or request.user.is_InternationalFinanceManager or request.user.is_InternationalSalesManager or request.user.is_ProductionManager or request.user.is_KiaProductionManager or request.user.is_KavoshProductionManager or request.user.is_FinancialManager_readonly or request.user.is_InternationalFinanceManager_readonly or request.user.is_InternationalSalesManager_readonly or request.user.is_ProductionManager_readonly or request.user.is_KiaProductionManager_readonly or request.user.is_KavoshProductionManager_readonly))

class hasGlobalSalesAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_superuser or request.user.is_global_sales_viewer))

class hasDetailedSalesAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_superuser or request.user.is_detailed_sales_viewer))
