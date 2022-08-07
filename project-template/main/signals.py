"""
Event listeners
"""

import logging

from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.contrib.auth import get_user_model

from main.threadlocals import current_request


security_logger = logging.getLogger("security")
User = get_user_model()


def log_login_success(sender, request, user, **kwargs):
    """
    Log login events (to admin)
    """

    security_logger.info(
        "Login success user_id=%s", user.id
    )


def log_login_failed(sender, credentials, **kwargs):
    """
    Log login events (to admin)
    """

    if "username" in credentials:
        security_logger.info(
            "Login failure for %s",
            User.objects.get(username=credentials["username"]).id
        )
    else:
        security_logger.info(
            "Login failure",
        )


def user_changed(
        sender,
        instance,
        created,
        raw,
        using,
        update_fields,
        **kwargs):
    """
    Log password change and user creation events
    """

    maybe_request = current_request()
    if maybe_request:
        if maybe_request.user.is_authenticated:
            creator = maybe_request.user.id
        else:
            # This shouldn't happen
            creator = "<unauthed user>"
    else:
        creator = "<unknown>"

    if created:
        security_logger.info(
            "User created %s by %s", instance.id, creator
        )
    elif instance._password:
        # The set_password method adds the _password property as a
        # side effect.
        security_logger.info(
            "User password changed %s by %s", instance.id, creator
        )


user_logged_in.connect(log_login_success)
user_login_failed.connect(log_login_failed)
post_save.connect(user_changed, sender=User)
