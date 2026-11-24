
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from reports.models import (
    Category,
    Report,
    ReportManagementToken,
    ReportImage,
)

from reports.services import (
    create_report,
    resolve_report,
    remove_report,
    update_report,
)



class ReportServiceTests(TestCase):

    def setUp(self):
       self.category, created = Category.objects.get_or_create(
    name="Phones"
)

       self.report_data = {
            "type": Report.ReportType.LOST,
            "title": "Samsung phone",
            "category": self.category,
            "description": "Black Samsung phone lost near Choba.",
            "occurred_at": timezone.now() - timedelta(hours=2),
            "phone_number": "08012345678",
            "latitude": 4.8156,
            "longitude": 7.0498,
            "location_name": "Choba, Port Harcourt",
            "location_accuracy": 10,
            "location_source": "gps",
        }


    def test_create_report_successfully(self):
        report, raw_token = create_report(
            data=self.report_data
        )

        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(report.title, "Samsung phone")
        self.assertEqual(report.type, Report.ReportType.LOST)
        self.assertEqual(report.status, Report.Status.ACTIVE)

        self.assertEqual(report.location.x, 7.0498)
        self.assertEqual(report.location.y, 4.8156)

        self.assertTrue(raw_token)

        token = ReportManagementToken.objects.get(
            report=report
        )

        self.assertEqual(
            token.token_hash,
            ReportManagementToken.hash_token(raw_token)
        )

        self.assertNotEqual(token.token_hash, raw_token)

    
    def test_create_report_rejects_invalid_latitude(self):
        invalid_data = self.report_data.copy()
        invalid_data["latitude"] = 95

        with self.assertRaisesMessage(
            ValueError,
            "Invalid latitude."
        ):
            create_report(data=invalid_data)

        self.assertEqual(Report.objects.count(), 0)
        self.assertEqual(ReportManagementToken.objects.count(), 0)

    
    def test_create_report_rejects_invalid_longitude(self):
        invalid_data = self.report_data.copy()
        invalid_data["longitude"] = 200

        with self.assertRaisesMessage(
            ValueError,
            "Invalid longitude."
        ):
            create_report(data=invalid_data)

        self.assertEqual(Report.objects.count(), 0)
        self.assertEqual(ReportManagementToken.objects.count(), 0)

    
    def test_create_report_rejects_more_than_five_images(self):
        images = [
            SimpleUploadedFile(
                f"image_{i}.jpg",
                b"fake-image-content",
                content_type="image/jpeg",
            )
            for i in range(6)
        ]

        with self.assertRaisesMessage(
            ValueError,
            "A report can have a maximum of 5 images."
        ):
            create_report(
                data=self.report_data,
                images=images,
            )

        self.assertEqual(Report.objects.count(), 0)
        self.assertEqual(ReportImage.objects.count(), 0)

    
    def test_create_report_with_five_images(self):
        images = [
            SimpleUploadedFile(
                f"image_{i}.jpg",
                b"fake-image-content",
                content_type="image/jpeg",
            )
            for i in range(5)
        ]

        report, raw_token = create_report(
            data=self.report_data,
            images=images,
        )

        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(ReportImage.objects.filter(report=report).count(), 5)

        saved_images = ReportImage.objects.filter(
            report=report
        ).order_by("display_order")

        self.assertEqual(
            list(saved_images.values_list("display_order", flat=True)),
            [0, 1, 2, 3, 4],
        )

        self.assertTrue(raw_token)

    
    def test_resolve_active_report(self):
        report, _ = create_report(
            data=self.report_data
        )

        resolved_report = resolve_report(report=report)

        self.assertEqual(
            resolved_report.status,
            Report.Status.RESOLVED
        )

        resolved_report.refresh_from_db()

        self.assertEqual(
            resolved_report.status,
            Report.Status.RESOLVED
        )

    
    def test_resolve_already_resolved_report(self):
        report, _ = create_report(
            data=self.report_data
        )

        report.status = Report.Status.RESOLVED
        report.save(update_fields=["status"])

        result = resolve_report(report=report)

        self.assertEqual(
            result.status,
            Report.Status.RESOLVED
        )

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            Report.Status.RESOLVED
        )



    def test_remove_active_report(self):
        report, _ = create_report(
            data=self.report_data
        )

        removed_report = remove_report(report=report)

        self.assertEqual(
            removed_report.status,
            Report.Status.REMOVED
        )

        removed_report.refresh_from_db()

        self.assertEqual(
            removed_report.status,
            Report.Status.REMOVED
        )

        # Soft removal: the database record still exists.
        self.assertTrue(
            Report.objects.filter(pk=report.pk).exists()
        )

    
    def test_remove_resolved_report_does_nothing(self):
        report, _ = create_report(
            data=self.report_data
        )

        report.status = Report.Status.RESOLVED
        report.save(update_fields=["status"])

        result = remove_report(report=report)

        self.assertEqual(
            result.status,
            Report.Status.RESOLVED
        )

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            Report.Status.RESOLVED
        )

        self.assertTrue(
            Report.objects.filter(pk=report.pk).exists()
        )


    
    def test_update_active_report(self):
        report, _ = create_report(
            data=self.report_data
        )

        updated_data = self.report_data.copy()
        updated_data.update({
            "title": "Updated Samsung phone",
            "description": "Black Samsung phone lost near Choba Junction.",
            "phone_number": "08098765432",
            "latitude": 4.8200,
            "longitude": 7.0600,
            "location_name": "Choba Junction",
            "location_accuracy": 15,
            "location_source": "map",
        })

        updated_report = update_report(
            report=report,
            data=updated_data,
        )

        updated_report.refresh_from_db()

        self.assertEqual(
            updated_report.title,
            "Updated Samsung phone"
        )

        self.assertEqual(
            updated_report.description,
            updated_data["description"]
        )

        self.assertEqual(
            updated_report.phone_number,
            "08098765432"
        )

        self.assertEqual(
            updated_report.location.x,
            7.0600
        )

        self.assertEqual(
            updated_report.location.y,
            4.8200
        )

        self.assertEqual(
            updated_report.location_name,
            "Choba Junction"
        )

        self.assertEqual(
            updated_report.location_source,
            "map"
        )


    def test_update_resolved_report_raises_error(self):
        report, _ = create_report(
            data=self.report_data
        )

        report.status = Report.Status.RESOLVED
        report.save(update_fields=["status"])

        updated_data = self.report_data.copy()
        updated_data["title"] = "Attempted update"

        with self.assertRaisesMessage(
            ValueError,
            "Only active reports can be edited."
        ):
            update_report(
                report=report,
                data=updated_data,
            )

        report.refresh_from_db()

        self.assertEqual(
            report.title,
            "Samsung phone"
        )

        self.assertEqual(
            report.status,
            Report.Status.RESOLVED
        )


    def test_update_report_rejects_invalid_latitude(self):
        report, _ = create_report(
            data=self.report_data
        )

        updated_data = self.report_data.copy()
        updated_data["latitude"] = 95

        with self.assertRaisesMessage(
            ValueError,
            "Invalid latitude."
        ):
            update_report(
                report=report,
                data=updated_data,
            )

        report.refresh_from_db()

        self.assertEqual(
            report.location.y,
            4.8156
        )

        self.assertEqual(
            report.title,
            "Samsung phone"
        )


    def test_update_report_rejects_invalid_longitude(self):
        report, _ = create_report(
            data=self.report_data
        )

        updated_data = self.report_data.copy()
        updated_data["longitude"] = 200

        with self.assertRaisesMessage(
            ValueError,
            "Invalid longitude."
        ):
            update_report(
                report=report,
                data=updated_data,
            )

        report.refresh_from_db()

        self.assertEqual(
            report.location.x,
            7.0498
        )

        self.assertEqual(
            report.title,
            "Samsung phone"
        )


    @patch(
        "reports.services._create_report_images",
        side_effect=ValueError("Image creation failed.")
    )
    def test_create_report_rolls_back_on_image_failure(self, mocked_images):
            with self.assertRaisesMessage(
                ValueError,
                "Image creation failed."
            ):
                create_report(data=self.report_data)

            self.assertEqual(Report.objects.count(), 0)
            self.assertEqual(ReportManagementToken.objects.count(), 0)



    def test_update_removed_report_raises_error(self):
        report, _ = create_report(
            data=self.report_data
        )

        report.status = Report.Status.REMOVED
        report.save(update_fields=["status"])

        updated_data = self.report_data.copy()
        updated_data["title"] = "Attempted update"

        with self.assertRaisesMessage(
            ValueError,
            "Only active reports can be edited."
        ):
            update_report(
                report=report,
                data=updated_data,
            )

        report.refresh_from_db()

        self.assertEqual(
            report.title,
            "Samsung phone"
        )

        self.assertEqual(
            report.status,
            Report.Status.REMOVED
        )


    def test_remove_already_removed_report_does_nothing(self):
        report, _ = create_report(
            data=self.report_data
        )

        report.status = Report.Status.REMOVED
        report.save(update_fields=["status"])

        result = remove_report(report=report)

        self.assertEqual(
            result.status,
            Report.Status.REMOVED
        )

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            Report.Status.REMOVED
        )

        self.assertTrue(
            Report.objects.filter(pk=report.pk).exists()
        )
