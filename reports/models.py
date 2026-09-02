# apps/reports/models.py

import uuid
import hashlib
import secrets

from django.contrib.gis.db import models
from django.core.validators import MinValueValidator
from django.db.models import Q




class Report(models.Model):
    class ReportType(models.TextChoices):
        LOST = "lost", "Lost"
        FOUND = "found", "Found"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RESOLVED = "resolved", "Resolved"
        REMOVED = "removed", "Removed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    type = models.CharField(
        max_length=10,
        choices=ReportType.choices,
        db_index=True,
    )

    title = models.CharField(
        max_length=150,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="reports",
    )

    description = models.TextField(
        max_length=2000,
    )

    location = models.PointField(
        geography=True,
        srid=4326,
    )

    location_name = models.CharField(
        max_length=255,
    )

    location_accuracy = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    location_source = models.CharField(
        max_length=20,
        choices=[
            ("gps", "GPS"),
            ("map", "Map"),
            ("search", "Search"),
        ],
        default="gps",
    )

    occurred_at = models.DateTimeField()

    phone_number = models.CharField(
        max_length=20,
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "type", "-created_at"]),
            models.Index(fields=["category", "status"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~Q(phone_number=""),
                name="report_phone_number_not_empty",
            ),
        ]

    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"
    

class ReportImage(models.Model):
    report = models.ForeignKey(
        "Report",
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="reports/%Y/%m/",
    )

    display_order = models.PositiveSmallIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["display_order", "created_at"]
        indexes = [
            models.Index(fields=["report", "display_order"]),
        ]

    def __str__(self):
        return f"Image for {self.report.title}"
    

class ReportManagementToken(models.Model):
    report = models.OneToOneField(
        "Report",
        on_delete=models.CASCADE,
        related_name="management_token",
    )

    token_hash = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["token_hash"]),
        ]

    def __str__(self):
        return f"Management token for {self.report.title}"

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(token.encode()).hexdigest()