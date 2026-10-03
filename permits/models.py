from django.conf import settings
from django.db import models

from master.models import (
    Location,
    PermitType,
    PPEItem,
    SafetyControl,
)


class Permit(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        REJECTED = "REJECTED", "Rejected"
        RESUBMITTED = "RESUBMITTED", "Resubmitted"
        APPROVED = "APPROVED", "Approved"
        CLOSED = "CLOSED", "Closed"
        CANCELLED = "CANCELLED", "Cancelled"

    permit_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
    )

    permit_type = models.ForeignKey(
        PermitType,
        on_delete=models.PROTECT,
        related_name="permits",
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="permits",
    )

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requested_permits",
    )

    work_description = models.TextField()

    contractor_name = models.CharField(
        max_length=200,
        blank=True,
    )

    workers = models.TextField(
        blank=True,
        help_text="Enter worker names, one per line.",
    )

    work_start = models.DateTimeField()

    work_end = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    rejection_reason = models.TextField(
        blank=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_permits",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    pdf_file = models.FileField(
        upload_to="permits/",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        if not self.permit_number:
            from django.utils import timezone

            year = timezone.now().year

            last = (
                Permit.objects
                .filter(
                    permit_number__startswith=f"PTW-{year}-"
                )
                .order_by("-id")
                .first()
            )

            if last:
                try:
                    number = int(
                        last.permit_number.split("-")[-1]
                    ) + 1
                except ValueError:
                    number = 1
            else:
                number = 1

            self.permit_number = (
                f"PTW-{year}-{number:05d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.permit_number


class PermitPPE(models.Model):

    permit = models.ForeignKey(
        Permit,
        on_delete=models.CASCADE,
        related_name="ppe_items",
    )

    ppe = models.ForeignKey(
        PPEItem,
        on_delete=models.PROTECT,
    )

    required = models.BooleanField(
        default=True,
    )

    verified = models.BooleanField(
        default=False,
    )

    remarks = models.CharField(
        max_length=500,
        blank=True,
    )

    class Meta:
        unique_together = ("permit", "ppe")

    def __str__(self):
        return f"{self.permit} - {self.ppe}"


class PermitSafetyControl(models.Model):

    permit = models.ForeignKey(
        Permit,
        on_delete=models.CASCADE,
        related_name="safety_controls",
    )

    safety_control = models.ForeignKey(
        SafetyControl,
        on_delete=models.PROTECT,
    )

    required = models.BooleanField(
        default=True,
    )

    verified = models.BooleanField(
        default=False,
    )

    remarks = models.CharField(
        max_length=500,
        blank=True,
    )

    class Meta:
        unique_together = (
            "permit",
            "safety_control",
        )

    def __str__(self):
        return (
            f"{self.permit} - "
            f"{self.safety_control}"
        )


class PermitReview(models.Model):

    class Action(models.TextChoices):
        APPROVE = "APPROVE", "Approve"
        REJECT = "REJECT", "Reject"

    permit = models.ForeignKey(
        Permit,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    safety_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    action = models.CharField(
        max_length=20,
        choices=Action.choices,
    )

    remarks = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.permit} - "
            f"{self.action}"
        )

