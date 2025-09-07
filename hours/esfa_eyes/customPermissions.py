from rest_framework import permissions


class hasEsfaEyesAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_superuser or request.user.is_FinancialManager or request.user.is_InternationalFinanceManager or request.user.is_InternationalSalesManager or request.user.is_InternationalSalesManager or request.user.is_ProductionManager))
