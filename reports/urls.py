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

    path(
        "home/",
        views.home,
        name="home",
    ),
    path(
        "list/",
        views.report_list,
        name="list",
    ),
       path(
        "<uuid:report_id>/contact/",
        views.report_contact,
        name="contact",
    ),

     path(
        "<uuid:report_id>/",
        views.report_detail,
        name="detail",
    ),

   path(
    "<uuid:report_id>/manage/<str:token>/",
    views.report_manage,
    name="manage",
),
    path(
    "<uuid:report_id>/manage/<str:token>/resolve/",
    views.report_resolve,
    name="resolve",
),

    path(
    "<uuid:report_id>/manage/<str:token>/remove/",
    views.report_remove,
    name="remove",
),

    path(
    "<uuid:report_id>/manage/<str:token>/edit/",
    views.report_edit,
    name="edit",
),
]