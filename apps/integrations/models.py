import uuid
from django.db import models

from .encryption import encrypt, decrypt


class GoogleCalendarConnection(models.Model):
    """Vínculo de um usuário com o Google Calendar, obtido via Auth0 (conexão
    social Google) só para essa integração — não é o login principal do app."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='google_calendar_connection')

    google_email = models.EmailField()
    scopes = models.CharField(max_length=500, blank=True)

    access_token = models.TextField()
    access_token_expires_at = models.DateTimeField()
    refresh_token_encrypted = models.TextField()

    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'google_calendar_connections'
        verbose_name = 'Conexão com Google Calendar'
        verbose_name_plural = 'Conexões com Google Calendar'

    def __str__(self):
        return f"{self.user} -> {self.google_email}"

    @property
    def refresh_token(self) -> str:
        return decrypt(self.refresh_token_encrypted)

    @refresh_token.setter
    def refresh_token(self, value: str) -> None:
        self.refresh_token_encrypted = encrypt(value)
