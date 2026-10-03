from django.db import models


class Location(models.Model):

    name = models.CharField(max_length=200)

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class PermitType(models.Model):

    name = models.CharField(
        max_length=200,
    )

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class PPEItem(models.Model):

    name = models.CharField(
        max_length=200,
    )

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class SafetyControl(models.Model):

    name = models.CharField(
        max_length=250,
    )

    description = models.TextField(
        blank=True,
    )

    active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.name


class PermitTypePPE(models.Model):

    permit_type = models.ForeignKey(
        PermitType,
        on_delete=models.CASCADE,
        related_name="ppe_configurations",
    )

    ppe = models.ForeignKey(
        PPEItem,
        on_delete=models.CASCADE,
        related_name="permit_configurations",
    )

    required = models.BooleanField(
        default=True,
    )

    class Meta:
        unique_together = ("permit_type", "ppe")

    def __str__(self):
        return (
            f"{self.permit_type} - "
            f"{self.ppe} - "
            f"{'Required' if self.required else 'Optional'}"
        )


class PermitTypeSafetyControl(models.Model):

    permit_type = models.ForeignKey(
        PermitType,
        on_delete=models.CASCADE,
        related_name="control_configurations",
    )

    safety_control = models.ForeignKey(
        SafetyControl,
        on_delete=models.CASCADE,
        related_name="permit_configurations",
    )

    required = models.BooleanField(
        default=True,
    )

    class Meta:
        unique_together = (
            "permit_type",
            "safety_control",
        )

    def __str__(self):
        return (
            f"{self.permit_type} - "
            f"{self.safety_control} - "
            f"{'Required' if self.required else 'Optional'}"
        )
