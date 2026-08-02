from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_CALENDAR_EVENTS_URL = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'


class IntegrationError(Exception):
    """Erro ao falar com Auth0 ou Google durante a integração de calendário."""


def _auth0_domain() -> str:
    if not settings.AUTH0_DOMAIN:
        raise IntegrationError('AUTH0_DOMAIN não configurado no backend.')
    return settings.AUTH0_DOMAIN


def exchange_auth0_code(code: str, redirect_uri: str) -> dict:
    """Troca o authorization code (fluxo de login social Google via Auth0) por tokens."""
    response = requests.post(f'https://{_auth0_domain()}/oauth/token', json={
        'grant_type': 'authorization_code',
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'code': code,
        'redirect_uri': redirect_uri,
    }, timeout=10)
    if not response.ok:
        raise IntegrationError(f'Falha ao trocar código com Auth0: {response.text}')
    return response.json()


def get_auth0_userinfo(auth0_access_token: str) -> dict:
    response = requests.get(
        f'https://{_auth0_domain()}/userinfo',
        headers={'Authorization': f'Bearer {auth0_access_token}'},
        timeout=10,
    )
    if not response.ok:
        raise IntegrationError(f'Falha ao buscar userinfo no Auth0: {response.text}')
    return response.json()


def _get_management_api_token() -> str:
    """Token client_credentials para a Management API do Auth0 — só é usado
    para ler o refresh_token do Google guardado na identity do usuário
    (o /userinfo não expõe tokens de conexões upstream)."""
    response = requests.post(f'https://{_auth0_domain()}/oauth/token', json={
        'grant_type': 'client_credentials',
        'client_id': settings.AUTH0_MGMT_CLIENT_ID,
        'client_secret': settings.AUTH0_MGMT_CLIENT_SECRET,
        'audience': f'https://{_auth0_domain()}/api/v2/',
    }, timeout=10)
    if not response.ok:
        raise IntegrationError(f'Falha ao autenticar na Management API do Auth0: {response.text}')
    return response.json()['access_token']


def get_google_identity(auth0_user_id: str) -> dict:
    """Busca a identity 'google-oauth2' do usuário no Auth0, que carrega o
    access_token/refresh_token do Google (exige que a conexão social use
    credenciais próprias do Google, não as dev keys, com offline access)."""
    mgmt_token = _get_management_api_token()
    response = requests.get(
        f'https://{_auth0_domain()}/api/v2/users/{auth0_user_id}',
        headers={'Authorization': f'Bearer {mgmt_token}'},
        params={'fields': 'identities,email', 'include_fields': 'true'},
        timeout=10,
    )
    if not response.ok:
        raise IntegrationError(f'Falha ao buscar identidade no Auth0: {response.text}')

    data = response.json()
    identity = next(
        (i for i in data.get('identities', []) if i.get('connection') == 'google-oauth2'),
        None,
    )
    if not identity or not identity.get('refresh_token'):
        raise IntegrationError(
            'Auth0 não retornou o refresh_token do Google. Confira se a conexão '
            'google-oauth2 usa um Google OAuth Client próprio (não as dev keys '
            'do Auth0) e se "Offline Access" está habilitado nela.'
        )

    return {
        'google_email': data.get('email', ''),
        'access_token': identity['access_token'],
        'refresh_token': identity['refresh_token'],
        'scopes': identity.get('access_token_scope', ''),
    }


def refresh_google_access_token(refresh_token: str) -> dict:
    response = requests.post(GOOGLE_TOKEN_URL, data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
    }, timeout=10)
    if not response.ok:
        raise IntegrationError(f'Falha ao renovar token do Google: {response.text}')
    return response.json()


def ensure_valid_access_token(connection) -> str:
    """Devolve um access_token válido, renovando direto com o Google (via
    refresh_token) quando o atual já expirou ou está perto de expirar."""
    if connection.access_token_expires_at > timezone.now() + timedelta(seconds=30):
        return connection.access_token

    tokens = refresh_google_access_token(connection.refresh_token)
    connection.access_token = tokens['access_token']
    connection.access_token_expires_at = timezone.now() + timedelta(seconds=tokens.get('expires_in', 3600))
    connection.save(update_fields=['access_token', 'access_token_expires_at', 'updated_at'])
    return connection.access_token


def fetch_calendar_events(connection, time_min: str | None = None, time_max: str | None = None) -> list:
    access_token = ensure_valid_access_token(connection)
    params = {'singleEvents': 'true', 'orderBy': 'startTime'}
    if time_min:
        params['timeMin'] = time_min
    if time_max:
        params['timeMax'] = time_max

    response = requests.get(
        GOOGLE_CALENDAR_EVENTS_URL,
        headers={'Authorization': f'Bearer {access_token}'},
        params=params,
        timeout=10,
    )
    if not response.ok:
        raise IntegrationError(f'Falha ao buscar eventos no Google Calendar: {response.text}')
    return response.json().get('items', [])
