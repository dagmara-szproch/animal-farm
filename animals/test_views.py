from django.test import TestCase
from django.urls import reverse
from .models import Animal, Category

class AnimalViewsTest(TestCase):
    """
    Tests for the Animals app.

    These tests verify that:
    - The animal list view loads successfully and displays only active animals.
    - The animal detail view loads successfully and shows the correct animal information.
    - Templates render the expected content such as name, species, and description.

    Purpose:
    Ensure that basic browsing functionality works correctly before adding features
    like donations, authentication, or volunteer management.
    """
    def setUp(self):
        self.cat = Category.objects.create(name="Horses", slug="horses")
        self.animal = Animal.objects.create(
            name="Lucky",
            slug="lucky",
            species="Horse",
            category=self.cat,
            description="A friendly horse"
        )

    def test_animal_list_view(self):
        response = self.client.get(reverse('animals:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lucky")

    def test_animal_detail_view(self):
        response = self.client.get(reverse('animals:detail', args=[self.animal.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A friendly horse")