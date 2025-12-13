from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from django.http import HttpResponseRedirect

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    FUTURE: Will implement role-based redirects.
    For now, Django uses default behavior via LOGIN_REDIRECT_URL.
    """
    pass

# class CustomAccountAdapter(DefaultAccountAdapter):
#     def get_login_redirect_url(self, request):
#         """
#         Implements your Post-Login Redirect Rules:
#         - Donor → Donor Dashboard
#         - Volunteer (pending) → Pending Volunteer Page
#         - Volunteer (approved) → Volunteer Dashboard
#         - Superuser → Django Admin
#         """
#         user = request.user

#         # Superusers go to admin
#         if user.is_superuser:
#             return reverse('admin:index')

#         # Volunteers
#         if user.role == 'volunteer':
#             if user.is_approved:
#                 return reverse('volunteer_dashboard')  # Will be in volunteers app
#             else:
#                 return reverse('volunteer_pending')    # Will be in volunteers app

#         # Donors (default)
#         return reverse('donor_dashboard')  # Will be in accounts or donations app

#     def save_user(self, request, user, form, commit=True):
#         """Handle role assignment during signup."""
#         user = super().save_user(request, user, form, commit=False)

#         # Check session flag for volunteer signup
#         if request.session.get('is_volunteer_signup'):
#             user.role = 'volunteer'
#             user.is_approved = False
#             # Clear the flag
#             request.session.pop('is_volunteer_signup', None)

#         if commit:
#             user.save()
#         return user
