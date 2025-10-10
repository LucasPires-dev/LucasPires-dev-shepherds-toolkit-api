import uuid
from django.db import models


class Notification(models.Model):
    """Sistema de notificações"""

    NOTIFICATION_TYPE_CHOICES = [
        ('reminder', 'Lembrete'),
        ('deadline', 'Prazo'),
        ('info', 'Informação'),
        ('warning', 'Aviso'),
        ('success', 'Sucesso'),
    ]

    ENTITY_TYPE_CHOICES = [
        ('goal', 'Meta'),
        ('event', 'Evento'),
        ('prayer', 'Oração'),
        ('sermon', 'Sermão'),
        ('member', 'Membro'),
        ('other', 'Outro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    related_entity_type = models.CharField(max_length=50, choices=ENTITY_TYPE_CHOICES,
                                           blank=True, null=True)
    related_entity_id = models.UUIDField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        """Marca notificação como lida"""
        self.is_read = True
        self.save(update_fields=['is_read'])
