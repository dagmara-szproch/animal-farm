from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class CustomUser(AbstractUser):
    """
    Extended user model for the Animal Rescue platform.

    This model replaces Django's default User model to add custom fields
    specific to the rescue farm operations. It supports two main user roles:
    donors and volunteers.

    Relationships:
        - One-to-One: UserProfile (through related_name 'userprofile')
        - One-to-Many: UserDeletionRequest (through related_name
        'userdeletionrequest_set')
        - Reverse relationships from allauth: emailaddress_set,
        socialaccount_set

    Key Features:
        - Role-based permissions (donor/volunteer)
        - Volunteer approval system
        - Soft deletion support
        - Communication preferences
    """

    ROLE_CHOICES = (
        ('donor', 'Donor'),
        ('volunteer', 'Volunteer'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES,
                            default='donor')
    is_approved = models.BooleanField(default=False)
    phone = models.CharField(max_length=30, blank=True, null=True)
    receive_updates = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username

    @property
    def is_volunteer(self):
        """
        Check if user is an approved volunteer.
        """
        return self.role == 'volunteer' and self.is_approved

    @property
    def is_donor(self):
        """
        Check if user is a donor.
        """
        return self.role == 'donor'

    def soft_delete(self):
        """Mark user as deleted without removing from database."""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()


class UserProfile(models.Model):
    """
    Extended profile information for users.

    This model stores additional information that doesn't belong in the
    authentication system. Separating profile data from authentication
    follows Django best practices.

    Relationships:
        - One-to-One: CustomUser (each user has exactly one profile)

    Key Features:
        - Volunteer-specific information storage
        - Profile image upload
        - Address and contact details
        - Admin notes
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    volunteer_experience = models.TextField(blank=True, null=True)
    preferred_tasks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class UserDeletionRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('cancelled', 'Cancelled'),  # Added option
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default="pending")
    notes = models.TextField(blank=True, null=True)  # For admin comments

    class Meta:
        ordering = ['-requested_at']
        verbose_name = 'User Deletion Request'
        verbose_name_plural = 'User Deletion Requests'

    def __str__(self):
        return f"Deletion request for {self.user.username}"

    def mark_processed(self):
        """Mark request as processed."""
        self.status = 'processed'
        self.processed_at = timezone.now()
        self.save()

    def cancel(self):
        """Cancel the deletion request."""
        self.status = 'cancelled'
        self.save()


# Simplified signal
@receiver(post_save, sender=CustomUser)
def manage_user_profile(sender, instance, created, **kwargs):
    """
    Create or update user profile when CustomUser is saved.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Update existing profile or create if missing
        UserProfile.objects.get_or_create(user=instance)
