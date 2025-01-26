import django_filters
import django_tables2
import crispy_forms.helper as crispy_helper
import crispy_forms.layout as crispy_layout
from django_filters.views import FilterView
from django.db.migrations.recorder import MigrationRecorder
from django.views.generic.base import TemplateView
from django.utils import timezone

from main.auth.mixins import LoginNotRequiredMixin, PermissionRequiredMixin
from main.tasks import background_task


class HomeView(LoginNotRequiredMixin, TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["time"] = timezone.now()

        from django.contrib import messages
        messages.add_message(self.request, messages.INFO, "Hello world.")

        background_task.defer(msg="hello")

        return context


class MigrationsListView(PermissionRequiredMixin, django_tables2.SingleTableMixin, FilterView):
    """
    Example demonstrating django filters, table2, and permissions
    """

    class MigrationsTable(django_tables2.Table):
        class Meta:
            model = MigrationRecorder.Migration
            fields = ("pk", "app", "name", "applied")

    class MigrationsFilter(django_filters.FilterSet):
        name = django_filters.CharFilter(lookup_expr="icontains")
        app = django_filters.ChoiceFilter(
            # Will be filled out later
            choices=[]
        )

        class Meta:
            model = MigrationRecorder.Migration
            fields = ["name", "app"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.filters["app"].extra["choices"] = [
                (row, row)
                for row in MigrationRecorder.Migration.objects.distinct("app").values_list("app", flat=True)
            ]


    paginate_by = 3
    permission_required = ["main.view_migrations"]
    template_name = "main/migrations_list.html"
    table_class = MigrationsTable
    filterset_class = MigrationsFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        filter_helper = crispy_helper.FormHelper()
        filter_helper.form_method = "get"
        filter_helper.add_input(crispy_layout.Submit('submit', 'Filter'))

        context["filter_helper"] = filter_helper

        return context
