from django.urls import path

from .views import (
    AICompletionView,
    AIUsageView,
    BillingCheckoutView,
    BillingPortalView,
    StripeWebhookView,
)

urlpatterns = [
    path('complete/', AICompletionView.as_view(), name='ai-complete'),
    path('usage/', AIUsageView.as_view(), name='ai-usage'),
    path('billing/checkout/', BillingCheckoutView.as_view(), name='ai-billing-checkout'),
    path('billing/portal/', BillingPortalView.as_view(), name='ai-billing-portal'),
    path('billing/webhook/', StripeWebhookView.as_view(), name='ai-billing-webhook'),
]
