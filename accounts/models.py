from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        EMPLOYEE = "EMPLOYEE", "Employee"
        CONTRACTOR = "CONTRACTOR", "Contractor"
        SAFETY = "SAFETY", "Safety Officer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )

    employee_id = models.CharField(
        max_length=50,
        blank=True,
    )

    department = models.CharField(
        max_length=100,
        blank=True,
    )

    company = models.CharField(
        max_length=200,
        blank=True,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    def __str__(self):
        return self.get_full_name() or self.username
