from django.db import models
from django.conf import settings
from animals.models import Animal


class Payment(models.Model):
    """
    Represents a single donation made via Stripe.

    This model is intentionally lightweight because the platform accepts
    donations only (no physical goods, no delivery, no billing address).

    Key responsibilities:
    - Store donation metadata returned from Stripe
    - Link a donation to an Animal (optional)
    - Link a donation to a registered user or guest donor
    - Store an optional donor message for public display
    - Support admin moderation of donor messages before publication

    Relationships:
    - Optional ForeignKey to CustomUser (AUTH_USER_MODEL)
        A donation may be made by a registered user or anonymously.
    - Optional ForeignKey to Animal
        Allows donations to be linked to a specific rescued animal.

    Stripe:
    - Payments are created via Stripe PaymentIntents
    - Card details are never stored in the database
    """

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
    )

    MESSAGE_STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    # User and Animal
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    animal = models.ForeignKey(
        Animal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Donation details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField()  # For receipt
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES, default='pending')

    # Donor message. Donor can be "Anonymous"
    donor_name = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    message_status = models.CharField(
        max_length=20,
        choices=MESSAGE_STATUS_CHOICES,
        default='pending'
    )
    message_approved_at = models.DateTimeField(blank=True, null=True)

    # Stripe fields
    stripe_payment_intent_id = models.CharField(max_length=255)
    stripe_customer_id = models.CharField(max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['animal', 'message_status']),
        ]

    def __str__(self):
        return f"£{self.amount} from {self.donor_name or 'Anonymous'}"

    @property
    def display_name(self):
        """
        Get display name: user's name, donor_name, or Anonymous.
        """
        if self.user and self.user.get_full_name():
            return self.user.get_full_name()
        return self.donor_name or "Anonymous"

    @property
    def has_approved_message(self):
        """
        Check if message is approved and not empty.
        """
        return (
            self.message_status == 'approved'
            and self.message.strip() != ''
        )

    def approve_message(self):
        """
        Approve the donor message.
        """
        from django.utils import timezone
        self.message_status = 'approved'
        self.message_approved_at = timezone.now()
        self.save()

    def reject_message(self):
        """
        Reject the donor message.
        """
        self.message_status = 'rejected'
        self.save()
