from django.views.generic.base import TemplateView
from django.utils import timezone


class HomeView(TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["time"] = timezone.now()

        from django.contrib import messages
        messages.add_message(self.request, messages.INFO, "Hello world.")

        return context
