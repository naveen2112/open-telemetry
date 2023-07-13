"""
Django views that handles user authentication, login, logout, and callback 
after authentication
"""
import logging

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from core import constants
from hubble import auth_helper
from hubble.models import User
from hubble_report import settings
from hubble_report.settings import ENV_NAME


def login(request):
    """
    To make sure correct authentication method is renderred
    """
    context = {}
    context["login_method"] = ENV_NAME  # This context variable will be used in template to
    # render correct authentication method
    context["ENVIRONMENT_DEVELOPMENT"] = constants.ENVIRONMENT_DEVELOPMENT
    return render(request, "auth/login.html", context)


def signin(request):
    """
    Authenticates the user
    """
    redirect_url = ""
    if ENV_NAME == constants.ENVIRONMENT_DEVELOPMENT:  # To ensure the authentication method
        if request.method == "POST":
            user_email = request.POST.get("email")
            if User.objects.filter(email=user_email).exists():
                user = User.objects.get(email=user_email)
                if user is not None:
                    auth_login(request, user)
                    redirect_url = redirect(
                        settings.LOGIN_REDIRECT_URL  # pylint: disable=no-member
                    )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"{user_email} is an invalid mail-id, please enter a valid mail-id.",
                )
                redirect_url = redirect("login")
        else:
            redirect_url = redirect("login")
    else:
        flow = auth_helper.get_sign_in_flow(request.get_host())
        try:
            request.session["auth_flow"] = flow
        except Exception as exception:
            logging.error("An error has been occured while login %s", exception)
        redirect_url = HttpResponseRedirect(flow["auth_uri"])
    return redirect_url


def signout(request):
    """
    Logout the user from application
    """
    auth_helper.remove_user_and_token(request)
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def callback(request):
    """
    Handles the callback after authentication
    """
    result = auth_helper.get_token_from_code(request)
    data = result["id_token_claims"]
    user_crendentials = data["preferred_username"]
    try:
        user = User.objects.get(email=user_crendentials)
    except Exception:
        user = None
    if user is not None:  # Checks whether the authenticated member is form Mallow or no,
        # by checking with Database
        auth_login(request, user)
        return redirect(settings.LOGIN_REDIRECT_URL)  # pylint: disable=no-member

    messages.add_message(
        request,
        messages.ERROR,
        f"{user_crendentials} is an invalid mail-id, please enter a valid mail-id.",
    )
    return redirect("login")


def health_check():
    """
    Performs a health check of the application
    """
    return JsonResponse(data="", status=200, safe=False)


def error_404(request):
    """
    Handles the 404 error (page not found)
    """
    return render(request, "errors/404.html")
