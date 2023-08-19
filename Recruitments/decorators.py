from django.contrib.auth.decorators import user_passes_test
import functools
from django.shortcuts import redirect

def superuser_required(view_func):
    """
    Decorator that requires the user to be a superuser.
    """
    return user_passes_test(lambda u: u.is_superuser)(view_func)


def staff_req(view_func):
    """
    Decorator that requires the user to be a staff member.
    """
    return user_passes_test(lambda u: u.is_staff, redirect_field_name="/")(view_func)
    # return user_passes_test(lambda u: u.is_staff)(view_func)