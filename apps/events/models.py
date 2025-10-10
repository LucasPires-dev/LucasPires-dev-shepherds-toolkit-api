import uuid
from django.db import models


class Event(models.Model):
    """Eventos e agenda"""

    EVENT_TYPE_CHOICES = [
        ('service', 'Culto'),
        ('meeting', 'Reunião'),
        ('study', 'Estudo Bíblico'),
        ('prayer', 'Oração'),
        ('visit', 'Visita'),
        ('other', 'Outro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=100, choices=EVENT_TYPE_CHOICES)
    location = models.CharField(max_length=255, blank=True, null=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    color = models.CharField(max_length=20, blank=True, null=True)
    reminder_minutes = models.IntegerField(blank=True, null=True,
                                           help_text="Minutos antes para lembrete")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['start_datetime']

    def __str__(self):
        return self.title

