"""
Generates a token to access the debug-http view.
"""

from django.core.management import BaseCommand
from django.core.signing import TimestampSigner


class Command(BaseCommand):
    """
    Generate a token to use the debug-http view
    """

    help = "Generate token for debug-http view"

    def handle(self, *args, **kwargs):
        signer = TimestampSigner(salt="DebugHttpView")
        print(signer.sign(""))
