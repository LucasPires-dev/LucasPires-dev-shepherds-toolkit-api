import hmac

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import GoogleCalendarConnection
from .serializers import (
    GoogleCalendarCallbackSerializer,
    GoogleCalendarStatusSerializer,
    KoinoniaTokenExchangeSerializer,
)

KOINONIA_CODE_SALT = 'koinonia-authorize'


class GoogleCalendarStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        connection = GoogleCalendarConnection.objects.filter(user=request.user).first()
        if not connection:
            return Response({'connected': False})
        return Response(GoogleCalendarStatusSerializer(connection).data)


class GoogleCalendarCallbackView(APIView):
    """Recebe o authorization code do redirect do Auth0 (conexão social
    Google) e conclui o vínculo, guardando o refresh_token do Google."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GoogleCalendarCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tokens = services.exchange_auth0_code(
                serializer.validated_data['code'],
                serializer.validated_data['redirect_uri'],
            )
            userinfo = services.get_auth0_userinfo(tokens['access_token'])
            identity = services.get_google_identity(userinfo['sub'])
        except services.IntegrationError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        connection, _ = GoogleCalendarConnection.objects.update_or_create(
            user=request.user,
            defaults={
                'google_email': identity['google_email'],
                'scopes': identity['scopes'],
                'access_token': identity['access_token'],
                # Tratado como já expirado: a próxima leitura renova direto
                # com o Google via refresh_token, sem depender do Auth0 nos dar um expires_in confiável aqui.
                'access_token_expires_at': timezone.now(),
            },
        )
        connection.refresh_token = identity['refresh_token']
        connection.save(update_fields=['refresh_token_encrypted'])

        return Response(GoogleCalendarStatusSerializer(connection).data, status=status.HTTP_201_CREATED)


class GoogleCalendarDisconnectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        GoogleCalendarConnection.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GoogleCalendarEventsView(APIView):
    """Proxy de leitura para os eventos do Google Calendar do usuário
    conectado. Não persiste nada em apps.events — isso fica para uma
    próxima etapa de sincronização de fato."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        connection = GoogleCalendarConnection.objects.filter(user=request.user).first()
        if not connection:
            return Response({'error': 'Google Calendar não conectado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            events = services.fetch_calendar_events(
                connection,
                time_min=request.query_params.get('time_min'),
                time_max=request.query_params.get('time_max'),
            )
        except services.IntegrationError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({'items': events})


class KoinoniaAuthorizeView(APIView):
    """Passo de consentimento do mini-OAuth interno: o usuário já está
    logado aqui (no shepherds-toolkit) e aprovou liberar acesso ao
    koinonia-app. Devolve um código de uso único e curta duração que o
    frontend repassa, via redirect, para o koinonia-app."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = signing.dumps(str(request.user.id), salt=KOINONIA_CODE_SALT)
        return Response({'code': code})


class KoinoniaTokenExchangeView(APIView):
    """Chamada servidor-a-servidor do Koinonia-Api: troca o código de uso
    único por um token de acesso do usuário, validando um segredo
    compartilhado entre os dois backends."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = KoinoniaTokenExchangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not hmac.compare_digest(serializer.validated_data['client_secret'], settings.KOINONIA_CLIENT_SECRET):
            return Response({'error': 'client_secret inválido.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user_id = signing.loads(serializer.validated_data['code'], salt=KOINONIA_CODE_SALT, max_age=300)
        except signing.BadSignature:
            return Response({'error': 'Código inválido ou expirado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'access_token': token.key, 'email': user.email})
