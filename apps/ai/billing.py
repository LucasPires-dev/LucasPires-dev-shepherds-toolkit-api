import stripe
from django.conf import settings

from .models import AIQuota

stripe.api_key = settings.STRIPE_SECRET_KEY

_ACTIVE_STATUSES = {'active', 'trialing'}


class BillingError(Exception):
    """Erro ao falar com o Stripe (chave ausente, price id inválido, etc)."""


def _require_configured():
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PRICE_ID_PRO:
        raise BillingError(
            'Stripe não está configurado (STRIPE_SECRET_KEY / STRIPE_PRICE_ID_PRO ausentes).'
        )


def get_or_create_stripe_customer(user):
    quota, _ = AIQuota.objects.get_or_create(user=user)
    if quota.stripe_customer_id:
        return quota.stripe_customer_id

    customer = stripe.Customer.create(email=user.email, name=user.get_full_name() or user.username)
    quota.stripe_customer_id = customer.id
    quota.save(update_fields=['stripe_customer_id', 'updated_at'])
    return customer.id


def create_checkout_session(user, success_url, cancel_url):
    _require_configured()
    customer_id = get_or_create_stripe_customer(user)
    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode='subscription',
        line_items=[{'price': settings.STRIPE_PRICE_ID_PRO, 'quantity': 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.url


def create_portal_session(user, return_url):
    _require_configured()
    quota = AIQuota.objects.filter(user=user).first()
    if not quota or not quota.stripe_customer_id:
        raise BillingError('Usuário ainda não possui um cliente Stripe (nenhuma assinatura iniciada).')

    session = stripe.billing_portal.Session.create(
        customer=quota.stripe_customer_id,
        return_url=return_url,
    )
    return session.url


def _sync_quota_from_subscription(quota, subscription):
    status = subscription['status']
    quota.stripe_subscription_id = subscription['id']
    quota.subscription_status = status
    quota.plan = 'pro' if status in _ACTIVE_STATUSES else 'free'
    quota.save(update_fields=['stripe_subscription_id', 'subscription_status', 'plan', 'updated_at'])


def handle_webhook_event(event):
    """Único ponto que altera AIQuota.plan a partir de pagamento — nunca o frontend."""
    event_type = event['type']
    data = event['data']['object']

    if event_type == 'checkout.session.completed':
        quota = AIQuota.objects.filter(stripe_customer_id=data['customer']).first()
        if quota and data.get('subscription'):
            subscription = stripe.Subscription.retrieve(data['subscription'])
            _sync_quota_from_subscription(quota, subscription)

    elif event_type in ('customer.subscription.updated', 'customer.subscription.created'):
        quota = AIQuota.objects.filter(stripe_customer_id=data['customer']).first()
        if quota:
            _sync_quota_from_subscription(quota, data)

    elif event_type == 'customer.subscription.deleted':
        quota = AIQuota.objects.filter(stripe_customer_id=data['customer']).first()
        if quota:
            quota.subscription_status = 'canceled'
            quota.plan = 'free'
            quota.save(update_fields=['subscription_status', 'plan', 'updated_at'])
