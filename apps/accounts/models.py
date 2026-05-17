from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    SUPER_ADMIN = "super_admin", "Super Admin"
    BRANCH_MANAGER = "branch_manager", "Branch Manager"
    FLEET_AUDITOR = "fleet_auditor", "Fleet Auditor"


class User(AbstractUser):
    tenant = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
        help_text="Null only for platform super admins.",
    )
    branch = models.ForeignKey(
        "tenants.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.FLEET_AUDITOR,
    )

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_super_admin(self) -> bool:
        return self.role == Role.SUPER_ADMIN

    @property
    def is_branch_manager(self) -> bool:
        return self.role == Role.BRANCH_MANAGER

    @property
    def is_fleet_auditor(self) -> bool:
        return self.role == Role.FLEET_AUDITOR
