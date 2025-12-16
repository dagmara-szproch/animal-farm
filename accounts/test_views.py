from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class DashboardViewTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_dashboard_requires_login(self):
        """Test that dashboard redirects to login if not authenticated"""
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertIn('/accounts/login/', response.url)

    def test_dashboard_loads_when_logged_in(self):
        """Test dashboard loads successfully for logged in user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/dashboard.html')

    def test_dashboard_context_data(self):
        """Test that dashboard view passes required context data"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:dashboard'))

        # Check all required context variables exist
        self.assertIn('donations', response.context)
        self.assertIn('total_donated', response.context)
        self.assertIn('total_donations', response.context)
        self.assertIn('animal_stats', response.context)
        self.assertIn('title', response.context)

        # Check types/values
        self.assertEqual(response.context['title'], 'My Dashboard')
        # No donations yet, so these should be zero/empty
        self.assertEqual(response.context['total_donated'], 0)
        # No donations yet, so these should be zero/empty
        self.assertEqual(response.context['total_donations'], 0)
        # No animal stats yet, so should be empty list
        self.assertEqual(len(response.context['animal_stats']), 0)
