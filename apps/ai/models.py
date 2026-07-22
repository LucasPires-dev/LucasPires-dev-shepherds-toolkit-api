import uuid
from django.db import models
from pgvector.django import VectorField


class AIQuota(models.Model):
    """Plano/cota de uso de IA de um usuário. Criado automaticamente
    quando o usuário é cadastrado (ver apps.ai.signals) — não é uma
    chave da OpenAI, é o registro que isola e limita o consumo dele."""

    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('unlimited', 'Unlimited'),
    ]

    SUBSCRIPTION_STATUS_CHOICES = [
        ('active', 'Ativa'),
        ('trialing', 'Em teste'),
        ('past_due', 'Pagamento atrasado'),
        ('canceled', 'Cancelada'),
        ('unpaid', 'Não paga'),
    ]

    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='ai_quota')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    stripe_customer_id = models.CharField(max_length=255, blank=True, default='')
    stripe_subscription_id = models.CharField(max_length=255, blank=True, default='')
    subscription_status = models.CharField(
        max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, blank=True, default=''
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_quotas'
        verbose_name = 'Cota de IA'
        verbose_name_plural = 'Cotas de IA'

    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()}"


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
    model = models.CharField(max_length=50, blank=True, default='')
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_interactions'
        verbose_name = 'Interação com IA'
        verbose_name_plural = 'Interações com IA'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_interaction_type_display()}"


class EmbeddingChunk(models.Model):
    """Pedaço de conteúdo pessoal do usuário (escrito, nota ou destaque de
    biblioteca) já transformado em embedding, pra busca semântica do Caleb.

    A tabela existe em qualquer backend (inclusive SQLite, pra não quebrar
    cascade delete de Writing/VerseNote/LibraryHighlight), mas só é
    populada/consultada de fato em Postgres com pgvector — em outros
    backends fica sempre vazia e o app usa o fallback por palavra-chave da
    Fase 1 (ver apps.ai.services._build_user_context)."""

    SOURCE_TYPE_CHOICES = [
        ('writing', 'Escrito'),
        ('verse_note', 'Nota de Versículo'),
        ('library_highlight', 'Destaque de Biblioteca'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='embedding_chunks')
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    writing = models.ForeignKey('writings.Writing', on_delete=models.CASCADE, null=True, blank=True, related_name='embedding_chunks')
    verse_note = models.ForeignKey('bible.VerseNote', on_delete=models.CASCADE, null=True, blank=True, related_name='embedding_chunks')
    library_highlight = models.ForeignKey('library.LibraryHighlight', on_delete=models.CASCADE, null=True, blank=True, related_name='embedding_chunks')
    chunk_index = models.PositiveIntegerField(default=0)
    content = models.TextField()
    embedding = VectorField(dimensions=1536)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_embedding_chunks'
        verbose_name = 'Pedaço de Embedding'
        verbose_name_plural = 'Pedaços de Embedding'

    def __str__(self):
        return f"{self.user.username} - {self.get_source_type_display()} #{self.chunk_index}"
