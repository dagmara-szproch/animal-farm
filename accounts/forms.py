from allauth.account.forms import SignupForm
from django import forms


class CustomSignupForm(SignupForm):
    """Add phone field to allauth signup."""
    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Phone (optional)'})
    )

    def save(self, request):
        user = super().save(request)
        user.phone = self.cleaned_data.get('phone', '')
        user.save()
        return user
