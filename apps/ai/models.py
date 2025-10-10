import uuid
from django.db import models


class AIInteraction(models.Model):
    """Histórico de interações com IA"""

    INTERACTION_TYPE_CHOICES = [
        ('context', 'Contexto'),
        ('etymology', 'Etimologia'),
        ('related_texts', 'Textos Relacionados'),
        ('application', 'Aplicação'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='ai_interactions')
    verse = models.ForeignKey('bible.BibleVerse', on_delete=models.SET_NULL,
                              blank=True, null=True, related_name='ai_interactions')
    interaction_type = models.CharField(max_length=50, choices=INTERACTION_TYPE_CHOICES)
    query = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_interactions'
        verbose_name = 'Interação com IA'
        verbose_name_plural = 'Interações com IA'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_interaction_type_display()}"
