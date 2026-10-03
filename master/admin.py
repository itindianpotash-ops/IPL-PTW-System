from django.contrib import admin

from .models import (
    Location,
    PermitType,
    PPEItem,
    SafetyControl,
    PermitTypePPE,
    PermitTypeSafetyControl,
)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "active",
    )

    search_fields = (
        "code",
        "name",
    )


@admin.register(PermitType)
class PermitTypeAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "active",
    )

    search_fields = (
        "code",
        "name",
    )


@admin.register(PPEItem)
class PPEItemAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "active",
    )

    search_fields = (
        "code",
        "name",
    )


@admin.register(SafetyControl)
class SafetyControlAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "active",
    )

    search_fields = (
        "name",
    )


@admin.register(PermitTypePPE)
class PermitTypePPEAdmin(admin.ModelAdmin):

    list_display = (
        "permit_type",
        "ppe",
        "required",
    )

    list_filter = (
        "permit_type",
        "required",
    )


@admin.register(PermitTypeSafetyControl)
class PermitTypeSafetyControlAdmin(admin.ModelAdmin):

    list_display = (
        "permit_type",
        "safety_control",
        "required",
    )

    list_filter = (
        "permit_type",
        "required",
    )
