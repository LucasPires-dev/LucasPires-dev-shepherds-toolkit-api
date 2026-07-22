import uuid
from django.db import models


class Writing(models.Model):
    """Registro de texto sobre a Palavra: sermão, devocional, esboço de estudo ou de livro"""

    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('completed', 'Concluído'),
        ('archived', 'Arquivado'),
    ]

    TYPE_CHOICES = [
        ('sermao', 'Sermão'),
        ('devocional', 'Devocional'),
        ('esboco_estudo', 'Esboço de Estudo'),
        ('esboco_livro', 'Esboço de Livro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='writings')
    title = models.CharField(max_length=500)
    content = models.TextField(blank=True, null=True)
    base_text = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: João 3:16")
    theme = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='sermao')
    preached_date = models.DateField(blank=True, null=True)
    estimated_duration = models.IntegerField(blank=True, null=True, help_text="Duração em minutos")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'writings'
        verbose_name = 'Escrito'
        verbose_name_plural = 'Escritos'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class WritingVerse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    writing = models.ForeignKey(Writing, on_delete=models.CASCADE, related_name='verses')
    verse = models.ForeignKey('bible.BibleVerse', on_delete=models.CASCADE)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'writing_verses'
        verbose_name = 'Versículo do Escrito'
        verbose_name_plural = 'Versículos do Escrito'
        ordering = ['order_index']

    def __str__(self):
        return f"{self.writing.title} - {self.verse.reference}"


class WritingTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'writing_tags'
        verbose_name = 'Tag de Escrito'
        verbose_name_plural = 'Tags de Escrito'

    def __str__(self):
        return self.name


class WritingTagRelation(models.Model):
    writing = models.ForeignKey(Writing, on_delete=models.CASCADE, related_name='tag_relations')
    tag = models.ForeignKey(WritingTag, on_delete=models.CASCADE, related_name='writing_relations')

    class Meta:
        db_table = 'writing_tag_relations'
        unique_together = ['writing', 'tag']
        verbose_name = 'Relação Escrito-Tag'
        verbose_name_plural = 'Relações Escrito-Tag'

    def __str__(self):
        return f"{self.writing.title} - {self.tag.name}"
