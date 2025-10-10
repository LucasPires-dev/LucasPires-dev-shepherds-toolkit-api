import uuid
from django.db import models


class PrayerRequest(models.Model):
    """Pedidos de oração"""

    CATEGORY_CHOICES = [
        ('personal', 'Pessoal'),
        ('church', 'Igreja'),
        ('missions', 'Missões'),
        ('health', 'Saúde'),
        ('family', 'Família'),
        ('financial', 'Financeiro'),
        ('other', 'Outro'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
    ]

    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('answered', 'Respondido'),
        ('archived', 'Arquivado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='prayer_requests')
    member = models.ForeignKey('members.Member', on_delete=models.SET_NULL,
                               blank=True, null=True, related_name='prayer_requests')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    is_confidential = models.BooleanField(default=False)
    answered_date = models.DateField(blank=True, null=True)
    answer_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prayer_requests'
        verbose_name = 'Pedido de Oração'
        verbose_name_plural = 'Pedidos de Oração'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

