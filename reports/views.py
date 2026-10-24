from django.shortcuts import render

# Create your views here.
from django.http import Http404
from django.shortcuts import render, redirect

from .forms import ReportCreateForm
from .models import Report
from .services import create_report

from django.http import JsonResponse
from django.conf import settings

from .geocoding import (
    GeocodingError,
    reverse_geocode,
)



def report_create(request, report_type=None):
    valid_types = {
        Report.ReportType.LOST,
        Report.ReportType.FOUND,
    }

    if report_type and report_type not in valid_types:
        raise Http404("Invalid report type.")

    if request.method == "POST":
        form = ReportCreateForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            try:
                report, raw_token = create_report(
                    data=form.cleaned_data,
                    images=request.FILES.getlist("images"),
                )

            except ValueError as error:
                form.add_error(None, str(error))

            else:
                request.session[
                    f"report_management_token_{report.id}"
                ] = raw_token

                return redirect(
                    "reports:create_success",
                    report_id=report.id,
                )

    else:
        initial = {}

        if report_type:
            initial["type"] = report_type

        form = ReportCreateForm(
            initial=initial,
        )

    return render(
        request,
        "reports/create_report.html",
        {
            "form": form,
            "report_type": report_type,
            "maptiler_api_key": settings.MAPTILER_API_KEY,
        },
    )

from django.shortcuts import get_object_or_404


def report_create_success(request, report_id):
    report = get_object_or_404(
        Report,
        id=report_id,
    )

    raw_token = request.session.get(
        f"report_management_token_{report.id}"
    )

    management_url = None

    if raw_token:
        management_url = request.build_absolute_uri(
            f"/reports/manage/{raw_token}/"
        )

    return render(
        request,
        "reports/create_success.html",
        {
            "report": report,
            "management_url": management_url,
        },
    )




def reverse_geocode_view(request):
    try:
        latitude = float(request.GET["lat"])
        longitude = float(request.GET["lon"])

    except (KeyError, TypeError, ValueError):
        return JsonResponse(
            {
                "error": "Invalid coordinates.",
            },
            status=400,
        )

    if not -90 <= latitude <= 90:
        return JsonResponse(
            {"error": "Invalid latitude."},
            status=400,
        )

    if not -180 <= longitude <= 180:
        return JsonResponse(
            {"error": "Invalid longitude."},
            status=400,
        )

    try:
        location_name = reverse_geocode(
            latitude=latitude,
            longitude=longitude,
        )

    except GeocodingError:
        return JsonResponse(
            {
                "error": (
                    "We found your position but could "
                    "not determine the place name."
                ),
            },
            status=502,
        )

    return JsonResponse(
        {
            "location_name": location_name,
        }
    )