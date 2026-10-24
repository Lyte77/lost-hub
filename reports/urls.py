from django.urls import path

from . import views


app_name = "reports"


urlpatterns = [
    path(
        "create/",
        views.report_create,
        name="create",
    ),

    path(
        "create/<str:report_type>/",
        views.report_create,
        name="create_by_type",
    ),

    path(
        "<uuid:report_id>/created/",
        views.report_create_success,
        name="create_success",
    ),

    path(
    "location/reverse-geocode/",
    views.reverse_geocode_view,
    name="reverse_geocode",
),
]