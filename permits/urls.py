from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.permit_list,
        name="permit_list",
    ),

    path(
        "create/",
        views.permit_create,
        name="permit_create",
    ),

    path(
        "<int:pk>/",
        views.permit_detail,
        name="permit_detail",
    ),

    path(
        "<int:pk>/edit/",
        views.permit_edit,
        name="permit_edit",
    ),

    path(
        "<int:pk>/review/",
        views.permit_review,
        name="permit_review",
    ),

    path(
        "ppe/<int:pk>/verify/",
        views.verify_ppe,
        name="verify_ppe",
    ),

    path(
        "control/<int:pk>/verify/",
        views.verify_control,
        name="verify_control",
    ),

    path(
        "<int:pk>/pdf/",
        views.permit_pdf,
        name="permit_pdf",
    ),
    path(
        "api/permit-types/<int:pk>/configuration/",
        views.permit_type_configuration,
        name="permit_type_configuration",
    ),

]
