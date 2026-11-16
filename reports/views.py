

# Create your views here.
import hmac
import hmac

from datetime import timezone
from django.urls import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.utils import timezone
from .utils import phone_for_whatsapp
from .selectors import get_managed_report
from django.views.decorators.http import require_GET, require_POST, require_POST
from .forms import ReportCreateForm, ReportUpdateForm
from .models import Category, Report, ReportManagementToken
from .services import create_report, remove_report, resolve_report, resolve_report, update_report
from .forms import ReportUpdateForm
from django.views.decorators.http import require_http_methods


from django.http import JsonResponse
from django.conf import settings

from .geocoding import (
    GeocodingError,
    reverse_geocode,
)

from .selectors import (
    get_public_report,
    get_public_reports,
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
    report = get_object_or_404(Report, id=report_id)

    management_token = request.session.get(
        f"report_management_token_{report.id}"
    )

    if not management_token:
        return HttpResponse("Management token not found in session.")

    management_url = reverse(
        "reports:manage",
        kwargs={
            "report_id": report.id,
            "token": management_token,
        }
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


def report_list(request):
    report_type = request.GET.get("type")
    category = request.GET.get("category")
    query = request.GET.get("q", "").strip()

    nearby = request.GET.get("nearby") == "1"

    latitude = None
    longitude = None

    try:
          if nearby:
              latitude = float(
                  request.GET.get("lat")
              )

              longitude = float(
                  request.GET.get("lon")
              )

    except (TypeError, ValueError):
          nearby = False


    try:
          radius_km = float(
              request.GET.get("radius", 5)
          )

    except (TypeError, ValueError):
          radius_km = 5


      # Prevent ridiculous requests such as 100000 km.
    radius_km = min(
          max(radius_km, 1),
          50,
      )


    reports = get_public_reports(
        report_type=report_type,
        category=category,
        query=query,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
    )

    paginator = Paginator(
        reports,
        12,
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    categories = (
        Category.objects
        .filter(is_active=True)
        .order_by("name")
    )

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "selected_type": report_type,
        "selected_category": category,
        "search_query": query,

        "nearby": nearby,
        "latitude": latitude,
        "longitude": longitude,
        "radius_km": radius_km,
    }

    if request.headers.get("HX-Request"):
        return render(
            request,
            "reports/partials/_report_results.html",
            context,
        )

    return render(
        request,
        "reports/report_list.html",
        context,
    )


def report_detail(request, report_id):
    report = get_public_report(
        report_id=report_id,
    )

    return render(
        request,
        "reports/report_detail.html",
        {
            "report": report,
        },
    )


def report_contact(request, report_id):
    report = get_public_report(
        report_id=report_id
    )
    whatsapp_number = phone_for_whatsapp(
        report.phone_number
    )

    return render(
        request,
        "reports/partials/_report_contact.html",
        {
            "report": report,
            "whatsapp_number": whatsapp_number
        },
    )


@require_GET
def report_manage(request, report_id, token):
    report = get_managed_report(
        report_id=report_id,
        raw_token=token,
    )

    # Record the successful management access.
    management_token = report.management_token
    management_token.last_used_at = timezone.now()
    management_token.save(update_fields=["last_used_at"])

    response = render(
        request,
        "reports/report_manage.html",
        {"report": report, "token": token,
         "is_active": report.status == Report.Status.ACTIVE,
         "is_resolved": report.status == Report.Status.RESOLVED,},
    )

    # Prevent sensitive management pages from being cached or
    # their URL being sent as a referrer to other websites.
    response["Cache-Control"] = "no-store"
    # response["Referrer-Policy"] = "no-referrer"
    response["X-Robots-Tag"] = "noindex, nofollow"

    return response

@require_POST
def report_resolve(request, report_id, token):
    # Verify ownership before performing the action.
    report = get_managed_report(
        report_id=report_id,
        raw_token=token,
    )

    resolve_report(report=report)

    return redirect(
        "reports:manage",
        report_id=report.id,
        token=token,
    )


@require_POST
def report_remove(request, report_id, token):
    report = get_managed_report(
        report_id=report_id,
        raw_token=token,
    )

    remove_report(report=report)

    return redirect(
        "reports:manage",
        report_id=report.id,
        token=token,
    )

@require_http_methods(["GET", "POST"])
def report_edit(request, report_id, token):
    report = get_managed_report(
        report_id=report_id,
        raw_token=token,
    )

    if report.status != Report.Status.ACTIVE:
        return redirect(
            "reports:manage",
            report_id=report.id,
            token=token,
        )

    if request.method == "POST":
        form = ReportUpdateForm(
            request.POST,
            instance=report,
        )

        if form.is_valid():
            try:
                update_report(
                    report=report,
                    data=form.cleaned_data,
                )
            except ValueError as error:
                form.add_error(None, str(error))
            else:
                return redirect(
                    "reports:manage",
                    report_id=report.id,
                    token=token,
                )

    else:
        form = ReportUpdateForm(instance=report)

    return render(
        request,
        "reports/edit_report.html",
        {
            "report": report,
            "form": form,
            "token": token,
            "initial_latitude": report.location.y,
            "initial_longitude": report.location.x,
            "initial_location_status": report.location_name,
            "maptiler_api_key": settings.MAPTILER_API_KEY,
        },
    )