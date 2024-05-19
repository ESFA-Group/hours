from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
import logging
from sheets.models import User

django_logger = logging.getLogger("django")


def signup(request):
    context = {
        "username": request.POST.get("username", ""),
        "first_name": request.POST.get("first_name", ""),
        "last_name": request.POST.get("last_name", ""),
    }

    if "signup_submit" in request.POST:

        if User.objects.filter(username=request.POST["username"]).exists():
            context.update({"existing_username": True})
            return render(request, "signup.html", context)

        if request.POST["password"] != request.POST["password_confirm"]:
            context.update({"wrong_confirm": True})
            return render(request, "signup.html", context)

        user = User.objects.create_user(
            username=request.POST["username"],
            password=request.POST["password"],
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
        )
        user.save()
        auth_login(request, user)
        django_logger.error(
            f"user with username '{user.username}' created successfully"
        )
        context.update({"created": True})

    return render(request, "signup.html", context)


def change_password(request):
    context = {
        "username": request.POST.get("username", ""),
    }
    if "change_password" in request.POST:

        user = authenticate(
            username=request.POST["username"], password=request.POST["oldPassword"]
        )

        if user is None:
            context.update({"not_authenticated": True})
            return render(request, "change_password.html", context)

        if request.POST["newPassword"] != request.POST["passwordConfirm"]:
            context.update({"wrong_confirm": True})
            return render(request, "change_password.html", context)

        user.set_password(request.POST["newPassword"])
        user.save()
        context.update({"password_changed": True})

    return render(request, "change_password.html", context)


def login(request):
    context = {
        "username": request.POST.get("username", ""),
    }
    if "login_submit" in request.POST:
        user = authenticate(
            username=request.POST["username"], password=request.POST["password"]
        )
        if user is not None:
            auth_login(request, user)
            return redirect(reverse("sheets:home_page"))
        else:
            context.update({"not_authenticated": True})

    return render(request, "login.html", context)


def logout(request):
    auth_logout(request)
    return redirect(reverse("sheets:login"))
