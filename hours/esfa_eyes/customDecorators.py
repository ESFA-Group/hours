from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy


decorators = [login_required(login_url=reverse_lazy("sheets:login"))]


def esfa_eyes_access_required(
    view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="admin:login"
):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.is_superuser or u.is_FinancialManager or u.is_InternationalFinanceManager or u.is_InternationalSalesManager or u.is_InternationalSalesManager or request.user.is_ProductionManager),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator