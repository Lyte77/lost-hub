# reports/services.py

from django.contrib.gis.geos import Point
from django.db import transaction

from .models import (
    Report,
    ReportImage,
    ReportManagementToken,
)


MAX_REPORT_IMAGES = 5


@transaction.atomic
def create_report(*, data, images=None):
    """
    Create a report, its images, and its private management token.

    Returns:
        tuple: (report, raw_management_token)
    """

    images = images or []

    if len(images) > MAX_REPORT_IMAGES:
        raise ValueError(
            f"A report can have a maximum of {MAX_REPORT_IMAGES} images."
        )

    latitude = data["latitude"]
    longitude = data["longitude"]

    location = _build_location_point(
        latitude=latitude,
        longitude=longitude,
    )

    report = Report.objects.create(
        type=data["type"],
        title=data["title"],
        category=data["category"],
        description=data["description"],
        occurred_at=data["occurred_at"],
        phone_number=data["phone_number"],

        location=location,
        location_name=data.get("location_name", ""),
        location_accuracy=data.get("location_accuracy"),
        location_source=data.get("location_source") or "gps",
    )

    _create_report_images(
        report=report,
        images=images,
    )

    raw_token = _create_management_token(report)

    return report, raw_token


def _build_location_point(*, latitude, longitude):
    if not -90 <= latitude <= 90:
        raise ValueError("Invalid latitude.")

    if not -180 <= longitude <= 180:
        raise ValueError("Invalid longitude.")

    return Point(
        longitude,
        latitude,
        srid=4326,
    )


def _create_report_images(*, report, images):
    for position, image in enumerate(images):
        ReportImage.objects.create(
            report=report,
            image=image,
            display_order=position,
        )


def _create_management_token(report):
    raw_token = ReportManagementToken.generate_token()

    ReportManagementToken.objects.create(
        report=report,
        token_hash=ReportManagementToken.hash_token(raw_token),
    )

    return raw_token