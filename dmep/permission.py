from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def is_cashier(user):
    # OPTION 1: simplest (staff but not superuser)
    return user.is_authenticated and user.is_staff