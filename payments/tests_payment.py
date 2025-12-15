from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from animals.models import Animal, Category
from payments.models import Payment

User = get_user_model()


class SimplePaymentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.animal = Animal.objects.create(
            name='Test Animal',
            slug='test-animal',  # This matches the URL
            species='Test Species',
            description='Test description',
            category=category
        )

    def test_login_required(self):
        """Test donation requires login"""
        response = self.client.get(
            reverse('payments:create_donation', args=[self.animal.slug])
        )
        self.assertEqual(response.status_code, 302)

    def test_authenticated_access(self):
        """Test authenticated users can access donation page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('payments:create_donation', args=[self.animal.slug])
        )
        self.assertEqual(response.status_code, 200)


class PaymentModelTests(TestCase):
    def test_str_representation(self):
        """Test Payment string representation"""
        payment = Payment(amount=25.00, donor_name='John Doe')
        self.assertTrue(str(payment).startswith("£"))
        self.assertTrue(str(payment).endswith("from John Doe"))
        self.assertIn("25", str(payment))

    def test_display_name_with_donor_name(self):
        """Test display_name uses donor_name"""
        payment = Payment(donor_name='Anonymous Donor')
        self.assertEqual(payment.display_name, 'Anonymous Donor')

    def test_has_approved_message_true(self):
        """Test has_approved_message returns True for approved messages"""
        payment = Payment(
            message='Test message',
            message_status='approved'
        )
        self.assertTrue(payment.has_approved_message)

    def test_has_approved_message_false(self):
        """Test has_approved_message returns False for pending messages"""
        payment = Payment(
            message='Test message',
            message_status='pending'
        )
        self.assertFalse(payment.has_approved_message)
