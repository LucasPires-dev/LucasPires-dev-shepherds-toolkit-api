import stripe
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bible.models import BibleVerse

from . import billing, services
from .serializers import AIRequestSerializer, AIResponseSerializer, AIUsageSerializer


class AICompletionView(APIView):
    """Proxy autenticado para a OpenAI. O cliente nunca vê a chave da API;
    cota e limite são aplicados por usuário no backend."""

    permission_classes = [IsAuthenticated]
    throttle_scope = 'ai'

    def post(self, request):
        request_serializer = AIRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data

        verse = None
        verse_id = data.get('verse_id')
        if verse_id is not None:
            verse = BibleVerse.objects.filter(pk=verse_id).first()

        try:
            interaction = services.run_ai_completion(
                user=request.user,
                interaction_type=data['interaction_type'],
                query=data['query'],
                verse=verse,
            )
        except services.QuotaExceededError as exc:
            return Response(
                {
                    'error': 'Limite mensal de IA do seu plano foi atingido.',
                    'plan': exc.plan,
                    'monthly_token_limit': exc.limit,
                    'tokens_used': exc.used,
                    'period_reset_at': exc.reset_at,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        except services.AIServiceError:
            return Response(
                {'error': 'Não foi possível obter uma resposta da IA agora. Tente novamente em instantes.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        usage = services.get_usage_summary(request.user)
        response_serializer = AIResponseSerializer({
            'response': interaction.response,
            'interaction_id': interaction.id,
            'created_at': interaction.created_at,
            'tokens_used': usage['tokens_used'],
            'tokens_remaining': usage['tokens_remaining'],
        })
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class AIUsageView(APIView):
    """Retorna o plano e o consumo do mês corrente do usuário autenticado."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        usage = services.get_usage_summary(request.user)
        serializer = AIUsageSerializer(usage)
        return Response(serializer.data)


class BillingCheckoutView(APIView):
    """Cria uma Stripe Checkout Session para o usuário assinar o plano Pro."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            checkout_url = billing.create_checkout_session(
                user=request.user,
                success_url=f'{settings.FRONTEND_URL}/billing?checkout=success',
                cancel_url=f'{settings.FRONTEND_URL}/billing?checkout=cancelled',
            )
        except billing.BillingError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({'checkout_url': checkout_url})


class BillingPortalView(APIView):
    """Cria uma sessão do Stripe Billing Portal para o usuário gerenciar a assinatura."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            portal_url = billing.create_portal_session(
                user=request.user,
                return_url=f'{settings.FRONTEND_URL}/billing',
            )
        except billing.BillingError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'portal_url': portal_url})


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Recebe eventos do Stripe. Autenticidade garantida pela assinatura
    Stripe-Signature, não por auth de usuário — é a única forma pela qual
    AIQuota.plan é promovido a 'pro'."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response({'error': 'Assinatura inválida'}, status=status.HTTP_400_BAD_REQUEST)

        billing.handle_webhook_event(event)
        return Response({'received': True})
