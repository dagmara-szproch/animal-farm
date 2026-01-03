from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('amount', 'display_name', 'animal', 'message_status', 'created_at')
    list_filter = ('message_status', 'status', 'animal')
    actions = ['approve_messages', 'reject_messages']

    def approve_messages(self, request, queryset):
        for payment in queryset:
            payment.approve_message()
        self.message_user(request, f"{queryset.count()} messages approved.")
    approve_messages.short_description = "Approve selected messages"

    def reject_messages(self, request, queryset):
        for payment in queryset:
            payment.reject_message()
        self.message_user(request, f"{queryset.count()} messages rejected.")
    reject_messages.short_description = "Reject selected messages"
