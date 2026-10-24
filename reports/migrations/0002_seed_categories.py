from django.db import migrations


CATEGORIES = [
    "Phones",
    "Wallets",
    "Keys",
    "Bags",
    "Documents",
    "Electronics",
    "Jewelry",
    "Clothing",
    "Pets",
    "Other",
]


def create_categories(apps, schema_editor):
    Category = apps.get_model("reports", "Category")

    for name in CATEGORIES:
        Category.objects.get_or_create(
            name=name,
            defaults={
                "slug": name.lower().replace(" ", "-"),
            },
        )


def remove_categories(apps, schema_editor):
    Category = apps.get_model("reports", "Category")

    Category.objects.filter(
        name__in=CATEGORIES
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_categories,
            remove_categories,
        ),
    ]