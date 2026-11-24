from reports.selectors import get_public_reports

from django.http import Http404
from datetime import timedelta
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.utils import timezone
from reports.selectors import get_public_report
from reports.models import Category, Report
from reports.selectors import get_public_reports

from reports.models import ReportManagementToken
from reports.selectors import get_managed_report


class PublicReportSelectorTests(TestCase):

    def setUp(self):
        self.phone_category, _ = Category.objects.get_or_create(
            name="Phones"
        )

        self.wallet_category, _ = Category.objects.get_or_create(
            name="Wallets"
        )

        self.active_report = Report.objects.create(
            type=Report.ReportType.LOST,
            title="Samsung phone",
            category=self.phone_category,
            description="Black Samsung phone lost near Choba.",
            occurred_at=timezone.now() - timedelta(hours=2),
            phone_number="08012345678",
            location_name="Choba, Port Harcourt",
            location=Point(7.0498, 4.8156, srid=4326),
        )

        self.resolved_report = Report.objects.create(
            type=Report.ReportType.LOST,
            title="Black wallet",
            category=self.wallet_category,
            description="Black leather wallet.",
            occurred_at=timezone.now() - timedelta(hours=3),
            phone_number="08087654321",
            location_name="Rumuokoro",
            location=Point(7.0120, 4.8500, srid=4326),
            status=Report.Status.RESOLVED,
        )

    def test_get_public_reports_returns_only_active_reports(self):
        reports = get_public_reports()

        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), self.active_report)

    def test_get_public_reports_filters_by_type(self):
        found_report = Report.objects.create(
            type=Report.ReportType.FOUND,
            title="Found iPhone",
            category=self.phone_category,
            description="Found an iPhone near Choba.",
            occurred_at=timezone.now() - timedelta(hours=1),
            phone_number="08098765432",
            location_name="Choba",
            location=Point(7.0500, 4.8160, srid=4326),
        )

        reports = get_public_reports(
            report_type=Report.ReportType.FOUND
        )

        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), found_report)

    def test_get_public_reports_filters_by_category(self):
        reports = get_public_reports(
            category=self.phone_category.slug
        )

        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), self.active_report)

    def test_get_public_reports_searches_by_title(self):
        reports = get_public_reports(query="Samsung")

        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), self.active_report)

    def test_get_public_reports_searches_by_description(self):
        reports = get_public_reports(query="Black Samsung")

        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), self.active_report)

    def test_get_public_reports_searches_by_category_name(self):
        reports = get_public_reports(query="Phones")

        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), self.active_report)

    def test_get_public_reports_searches_by_location_name(self):
        reports = get_public_reports(query="Choba")

        self.assertEqual(reports.count(), 1)
        self.assertEqual(reports.first(), self.active_report)

    def test_get_public_reports_orders_newest_first(self):
        older_report = Report.objects.create(
            type=Report.ReportType.LOST,
            title="Older phone",
            category=self.phone_category,
            description="An older phone report.",
            occurred_at=timezone.now() - timedelta(days=2),
            phone_number="08011111111",
            location_name="Choba",
            location=Point(7.0498, 4.8156, srid=4326),
        )

        newer_report = Report.objects.create(
            type=Report.ReportType.LOST,
            title="Newer phone",
            category=self.phone_category,
            description="A newer phone report.",
            occurred_at=timezone.now() - timedelta(hours=1),
            phone_number="08022222222",
            location_name="Choba",
            location=Point(7.0498, 4.8156, srid=4326),
        )

        base_time = timezone.now()

        older_report.created_at = base_time - timedelta(days=2)
        older_report.save(update_fields=["created_at"])

        self.active_report.created_at = base_time - timedelta(days=1)
        self.active_report.save(update_fields=["created_at"])

        newer_report.created_at = base_time
        newer_report.save(update_fields=["created_at"])

        reports = list(get_public_reports())

        self.assertEqual(
            reports,
            [newer_report, self.active_report, older_report],
        )

    def test_get_public_reports_filters_by_nearby_location(self):
        nearby_report = self.active_report

        far_report = Report.objects.create(
            type=Report.ReportType.LOST,
            title="Laptop lost far away",
            category=self.phone_category,
            description="Laptop lost in another area.",
            occurred_at=timezone.now() - timedelta(hours=1),
            phone_number="08033333333",
            location_name="Far location",
            location=Point(7.1500, 4.9500, srid=4326),
        )

        reports = get_public_reports(
            latitude=4.8156,
            longitude=7.0498,
            radius_km=5,
        )

        self.assertIn(nearby_report, reports)
        self.assertNotIn(far_report, reports)


    def test_get_public_reports_orders_nearby_by_distance(self):
        closer_report = Report.objects.create(
            type=Report.ReportType.LOST,
            title="Nearby wallet",
            category=self.wallet_category,
            description="Wallet lost close to Choba.",
            occurred_at=timezone.now() - timedelta(hours=1),
            phone_number="08033333333",
            location_name="Near Choba",
            location=Point(7.0500, 4.8160, srid=4326),
        )

        farther_report = Report.objects.create(
            type=Report.ReportType.LOST,
            title="Farther wallet",
            category=self.wallet_category,
            description="Wallet lost farther from Choba.",
            occurred_at=timezone.now() - timedelta(hours=2),
            phone_number="08044444444",
            location_name="Farther Choba",
            location=Point(7.0600, 4.8250, srid=4326),
        )

        reports = list(
            get_public_reports(
                latitude=4.8156,
                longitude=7.0498,
                radius_km=5,
            )
        )

        self.assertEqual(reports[0], self.active_report)
        self.assertEqual(reports[1], closer_report)
        self.assertEqual(reports[2], farther_report)

    def test_get_public_report_returns_active_report(self):
        report = get_public_report(
            report_id=self.active_report.id
        )

        self.assertEqual(report, self.active_report)
        self.assertEqual(report.status, Report.Status.ACTIVE)

    def test_get_public_report_does_not_return_removed_report(self):
        self.active_report.status = Report.Status.REMOVED
        self.active_report.save(update_fields=["status"])

        with self.assertRaises(Http404):
            get_public_report(
                report_id=self.active_report.id
            )

class ManagedReportSelectorTests(TestCase):

    def setUp(self):
        self.category, _ = Category.objects.get_or_create(
            name="Phones"
        )

        self.report = Report.objects.create(
            type=Report.ReportType.LOST,
            title="Samsung phone",
            category=self.category,
            description="Black Samsung phone lost near Choba.",
            occurred_at=timezone.now() - timedelta(hours=2),
            phone_number="08012345678",
            location_name="Choba, Port Harcourt",
            location=Point(7.0498, 4.8156, srid=4326),
        )

        self.raw_token = ReportManagementToken.generate_token()

        self.management_token = ReportManagementToken.objects.create(
            report=self.report,
            token_hash=ReportManagementToken.hash_token(
                self.raw_token
            ),
        )

    def test_get_managed_report_accepts_valid_token(self):
        report = get_managed_report(
            report_id=self.report.id,
            raw_token=self.raw_token,
        )

        self.assertEqual(report, self.report)

    def test_get_managed_report_rejects_invalid_token(self):
        invalid_token = "this-is-not-the-correct-token"

        with self.assertRaises(Http404):
            get_managed_report(
                report_id=self.report.id,
                raw_token=invalid_token,
            )

    def test_get_managed_report_rejects_revoked_token(self):
        self.management_token.revoked_at = timezone.now()
        self.management_token.save(update_fields=["revoked_at"])

        with self.assertRaises(Http404):
            get_managed_report(
                report_id=self.report.id,
                raw_token=self.raw_token,
            )

    def test_get_managed_report_rejects_expired_token(self):
        self.management_token.expires_at = (
            timezone.now() - timedelta(days=1)
        )
        self.management_token.save(update_fields=["expires_at"])

        with self.assertRaises(Http404):
            get_managed_report(
                report_id=self.report.id,
                raw_token=self.raw_token,
            )

    def test_get_managed_report_accepts_token_without_expiration(self):
        self.management_token.expires_at = None
        self.management_token.save(update_fields=["expires_at"])

        report = get_managed_report(
            report_id=self.report.id,
            raw_token=self.raw_token,
        )

        self.assertEqual(report, self.report)

    def test_get_managed_report_rejects_report_without_token(self):
        self.management_token.delete()

        with self.assertRaises(Http404):
            get_managed_report(
                report_id=self.report.id,
                raw_token=self.raw_token,
            )

    def test_get_managed_report_rejects_nonexistent_report(self):
        import uuid

        nonexistent_id = uuid.uuid4()

        with self.assertRaises(Http404):
            get_managed_report(
                report_id=nonexistent_id,
                raw_token=self.raw_token,
            )