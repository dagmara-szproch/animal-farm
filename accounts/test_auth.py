from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class AuthTests(TestCase):
    """
    Simple authentication tests for AnimalRescue.
    """

    def test_login_page_loads(self):
        """Test that login page loads with our custom template."""
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AnimalRescue')

    def test_signup_page_loads(self):
        """Test that signup page loads."""
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')

    def test_create_user_with_username(self):
        """Create user with username (since AbstractUser requires it)."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='donor'
        )

        self.assertEqual(user.role, 'donor')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))

    def test_create_volunteer(self):
        """Create volunteer user."""
        user = User.objects.create_user(
            username='volunteer1',
            email='volunteer@example.com',
            password='volpass123',
            role='volunteer',
            is_approved=False
        )

        self.assertEqual(user.role, 'volunteer')
        self.assertFalse(user.is_approved)

    def test_user_str_method(self):
        """Test the __str__ method."""
        user = User.objects.create_user(
            username='strtest',
            email='str@example.com',
            password='pass123'
        )
        self.assertEqual(str(user), 'strtest')

    def test_donor_login_redirect(self):
        """Test donor can log in successfully."""
        # Create user
        user = User.objects.create_user(
            username='donortest',
            email='donor@example.com',
            password='pass123',
            role='donor'
        )

        print(f"\n=== Testing donor login ===")
        print(f"Created user: {user.username}, email: {user.email}")

        # Try to login - Allauth expects 'login' field for email
        response = self.client.post(reverse('account_login'), {
            'login': 'donor@example.com',
            'password': 'pass123',
        }, follow=False)  # Don't follow redirects yet

        print(f"Login response status: {response.status_code}")
        print(f"Redirect URL: {getattr(response, 'url', 'No redirect')}")

        # Debug: Check what's in the response
        if response.status_code != 302:
            print(f"Response content snippet: {response.content[:200]}")

        # Allauth should redirect (302) after successful login
        # But if there are errors, it returns 200 with form errors
        if response.status_code == 200:
            # Check for form errors
            if hasattr(response, 'context') and 'form' in response.context:
                form = response.context['form']
                print(f"Form errors: {form.errors}")

        # The key assertion: login should work (either redirect or stay on
        # page with user logged in)
        # Check if user is in session
        user_id = self.client.session.get('_auth_user_id')
        print(f"User ID in session: {user_id}")

        # Either we got a redirect OR user is in session
        self.assertTrue(response.status_code == 302 or user_id is not None)

    def test_volunteer_pending_access(self):
        """Test pending volunteer can log in."""
        user = User.objects.create_user(
            username='pendingvol',
            email='pending@example.com',
            password='pass123',
            role='volunteer',
            is_approved=False
        )

        print(f"\n=== Testing volunteer login ===")

        # Login using the standard Django login (bypasses allauth form)
        login_success = self.client.login(username='pendingvol',
                                          password='pass123')
        print(f"Standard login success: {login_success}")

        # Check session
        user_id = self.client.session.get('_auth_user_id')
        print(f"User ID in session: {user_id}")

        self.assertTrue(login_success)
        self.assertEqual(int(user_id), user.id)

        # Make a request
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
