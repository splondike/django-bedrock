from django.views.generic.base import TemplateView
from django.utils import timezone

from main.auth.mixins import LoginNotRequiredMixin, PermissionRequiredMixin


class HomeView(LoginNotRequiredMixin, TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["time"] = timezone.now()

        from django.contrib import messages
        messages.add_message(self.request, messages.INFO, "Hello world.")

        return context


class MigrationsListView(PermissionRequiredMixin, TemplateView):
    """
    Example demonstrating django filters, table2, and permissions
    """

    permission_required = ["main.view_migrations"]

    template_name = "main/migrations_list.html"
