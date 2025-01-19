"""
Authorization framework based on the built in Django one.

For normal usage you'll be using the mixin.PermissionRequiredMixin and 
LoginNotRequiredMixin classes to do authorization in your views. You'll
also be using the built in perms sytem in templates: https://docs.djangoproject.com/en/5.1/topics/auth/default/#permissions .

During setup, for each type of authorization principal (i.e. user,
API token) in your system create an instance of AuthenticationPrincipal and
put it in instances.py along with the permission checks it needs. If
you're using API token principals you will also need to edit
auth/middleware.py to create an instance.

Some words on the thinking behind this system. The Django authorization
interface (has_perm etc.) is fine, but I've almost never used its
database based system for assigning groups and permissions. Instead I've 
preferred to be more direct and explicit by coding up the rules.

So the setup in this starter project is to remove the django.contrib.auth app
and get you to code up your own authorization logic. You use the same
authorization interface however since it's fine and lets you use e.g. Django
admin straightforwardly.

This module also includes a couple of extra helpers to make auth checks easier.
"""

from typing import Iterable, List, Optional

from django.db import models


class AuthenticationPrincipal:
    """
    An actor/principal whose access needs to be checked.

    Contains the important authorization methods from django.contrib.auth.models.PermissionMixin and django.contrib.auth.base_user.AbstractBaseUser .
    """

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Is this principal authenticated (i.e. logged in)?
        """

        return True

    def has_perm(self, perm: str, obj=Optional[models.Model]) -> bool:
        """
        Main permission check method. Usage:

            # Does the principal have this non-instance specific permission
            request.user.has_perm("main.my_custom_perm")

            # Does the principal have this permission on this instance of
            # the object
            request.user.has_perm("main.my_custom_perm", obj=something)

        Note that the permission labels are app_label.permission. This is
        the Django way of doing it.
        """

        return False

    def has_perms(self, perm_list: List[str], obj=Optional[models.Model]):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.

        Potentially allows for optimisations for bulk checking.
        """
        if not isinstance(perm_list, Iterable) or isinstance(perm_list, str):
            raise ValueError("perm_list must be an iterable of permissions.")
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label: str):
        """
        Return True if the user has any permissions in the given app label.
        Use similar logic as has_perm(), above.

        Kept for compatibility with Django's built in permission system.
        """

        return False

    def principal_logging_identifier(self) -> str:
        """
        A string that can be used to identify this principal and is also
        safe to send to logs (i.e. probably not the email address).
        """

        raise NotImplementedError
