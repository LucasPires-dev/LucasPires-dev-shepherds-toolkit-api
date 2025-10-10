import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Modelo customizado de usuário"""

    ROLE_CHOICES = [
        ('pastor', 'Pastor'),
        ('leader', 'Líder'),
        ('member', 'Membro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    church_name = models.CharField(max_length=255, blank=True, null=True)
    ministry = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='pastor')
    avatar_url = models.URLField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.get_full_name()} - {self.church_name}"
