from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            "PTW Information",
            {
                "fields": (
                    "role",
                    "employee_id",
                    "department",
                    "company",
                    "phone",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "PTW Information",
            {
                "fields": (
                    "role",
                    "employee_id",
                    "department",
                    "company",
                    "phone",
                )
            },
        ),
    )
