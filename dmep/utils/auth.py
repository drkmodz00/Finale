# utils/auth.py
from django.shortcuts import redirect

def cashier_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return redirect("login")

        if request.session.get("role") != "admin":
            return redirect("dashboard")

        return view_func(request, *args, **kwargs)
    return wrapper