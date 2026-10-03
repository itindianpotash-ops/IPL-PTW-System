from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "created_at",
        "user",
        "action",
        "model_name",
        "object_id",
    )

    list_filter = (
        "action",
        "model_name",
    )

    readonly_fields = (
        "user",
        "action",
        "model_name",
        "object_id",
        "description",
        "created_at",
    )
