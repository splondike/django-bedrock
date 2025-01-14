from django.contrib import admin
from django.urls import path

from main.views.util import (
    HealthcheckView,
    DebugHttpView,
    CspReportView,
    JsErrorReportView
)
from main.views.pages import HomeView
from main.views.error import server_error, bad_request, not_found, forbidden
# Ensure the signals are hooked up
import main.signals  # noqa: E262, F401, E402

urlpatterns = [
    path("", HomeView.as_view()),

    path("admin/", admin.site.urls),

    # Debug
    path("healthcheck", HealthcheckView.as_view()),
    path("debug-http", DebugHttpView.as_view()),
    path("csp-report", CspReportView.as_view(), name="csp_report"),
    path("js-error", JsErrorReportView.as_view(), name="js_error"),
    path("errors/400", bad_request, {"exception": Exception()}),
    path("errors/404", not_found, {"exception": Exception()}),
    path("errors/500", server_error),
]

handler500 = server_error
handler404 = not_found
handler400 = bad_request
handler403 = bad_request
