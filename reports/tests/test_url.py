from django.conf import settings
from django.test import SimpleTestCase
from django.urls import Resolver404, resolve


class MediaServingTests(SimpleTestCase):
    def test_media_route_is_enabled_only_in_debug(self):
        media_path = f"{settings.MEDIA_URL}missing-image.jpg"

        if settings.DEBUG:
            resolve(media_path)
        else:
            with self.assertRaises(Resolver404):
                resolve(media_path)