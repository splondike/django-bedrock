"""
Command to populate the database with dummy data for development
"""

from django.core.management import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    """
    Populate database with dummy data
    """

    help = "Populate DB with dummy data"

    def handle(self, *args, **kwargs):
        seeddb()


@transaction.atomic
def seeddb():
    user = User(email="user@example.com")
    user.set_password("password")
    user.save()
