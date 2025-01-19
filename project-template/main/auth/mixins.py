import logging
from typing import Iterable

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import ImproperlyConfigured


security_logger = logging.getLogger("security")


class PermissionRequiredMixin(AccessMixin):
    """
    A mixin that will assert the permissions of the AuthenticationPrincipal
    performing the request match what is specified. Clones the interface of
    the mixin of the same name from django-guardian and takes a bunch of
    code from that too.

    Does a bit more logging around permission failures since OWASP
    recommends that. See OWASP ASVS v4.0.3 items 7.1.3 and 7.2.2 .
    """

    def get_required_permissions(self, request=None):
        """
        Returns list of permissions in format *<app_label>.<codename>* that
        should be checked against *request.user* and *object*. By default, it
        returns list from ``permission_required`` attribute.

        :param request: Original request.
        """
        if isinstance(self.permission_required, str):
            perms = [self.permission_required]
        elif isinstance(self.permission_required, Iterable):
            perms = [p for p in self.permission_required]
        else:
            raise ImproperlyConfigured("'PermissionRequiredMixin' requires "
                                       "'permission_required' attribute to be set to "
                                       "'<app_label>.<permission codename>' but is set to '%s' instead"
                                       % self.permission_required)
        return perms

    def get_permission_object(self):
        if hasattr(self, 'permission_object'):
            return self.permission_object
        return (hasattr(self, 'get_object') and self.get_object() or
                getattr(self, 'object', None))

    def check_permissions(self, request, *args, **kwargs):
        """
        Checks if *request.user* has all permissions returned by
        *get_required_permissions* method.

        :param request: Original request.
        """
        perms = self.get_required_permissions(request)
        obj = self.get_permission_object()

        result = request.user.has_perms(perms, obj)
        if not result:
            for perm in perms:
                if not request.user.has_perm(perm, obj):
                    # Just log the first one
                    security_logger.warning(
                        "Permission denied: perm=%s, obj=%s, viewclass=%s",
                        perm,
                        obj,
                        self
                    )
                    break
            return self.handle_no_permission()
        else:
            security_logger.debug("Permission granted: viewclass=%s", self)
            return None

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        response = self.check_permissions(request, *args, **kwargs)
        if response:
            return response
        return super().dispatch(request, *args, **kwargs)


class LoginNotRequiredMixin:
    """
    Mixin for Views to indicate they don't require authentication
    and haven't just been forgotten. See auth/checks.py for where this is used.
    """
