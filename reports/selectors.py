from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Report
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils import timezone
import hmac
from .models import Report, ReportManagementToken


def get_public_reports(*,
                        report_type=None,
                          category=None,
                            query=None,
                            latitude=None,
                            longitude=None,
                            radius_km=5,):
    reports = (
        Report.objects
        .filter(status=Report.Status.ACTIVE)
        .select_related("category")
        .prefetch_related("images")
    )

    if report_type:
        reports = reports.filter(
            type=report_type
        )

    if category:
        reports = reports.filter(
            category__slug=category
        )

    if query:
        reports = reports.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(location_name__icontains=query)
        )

    
    if latitude is not None and longitude is not None:
        user_location = Point(
            longitude,
            latitude,
            srid=4326,
        )

        reports = (
            reports
            .filter(
                location__distance_lte=(
                    user_location,
                    D(km=radius_km),
                )
            )
            .annotate(
                distance=Distance(
                    "location",
                    user_location,
                )
            )
            .order_by("distance")
        )

        return reports


    return reports.order_by("-created_at")


def get_public_report(*, report_id):
    return get_object_or_404(
        Report.objects
        .filter(status=Report.Status.ACTIVE)
        .select_related("category")
        .prefetch_related("images"),
        id=report_id,
    )


def get_managed_report(*, report_id, raw_token):
    report = get_object_or_404(
        Report.objects.select_related("category"),
        id=report_id,
    )

    try:
        management_token = report.management_token
    except ReportManagementToken.DoesNotExist:
        raise Http404


    # Token has been manually revoked.
    if management_token.revoked_at is not None:
        raise Http404


    # Token has expired.
    if (
        management_token.expires_at is not None
        and management_token.expires_at <= timezone.now()
    ):
        raise Http404


    submitted_hash = (
        ReportManagementToken.hash_token(
            raw_token
        )
    )


    if not hmac.compare_digest(
        submitted_hash,
        management_token.token_hash,
    ):
        raise Http404


    return report