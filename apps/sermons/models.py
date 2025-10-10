import uuid
from django.db import models

class Sermon(models.Model):
    """Sermões criados pelos pastores"""

    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('completed', 'Concluído'),
        ('archived', 'Arquivado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sermons')
    title = models.CharField(max_length=500)
    content = models.TextField(blank=True, null=True)
    base_text = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: João 3:16")
    theme = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    preached_date = models.DateField(blank=True, null=True)
    estimated_duration = models.IntegerField(blank=True, null=True, help_text="Duração em minutos")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sermons'
        verbose_name = 'Sermão'
        verbose_name_plural = 'Sermões'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class SermonVerse(models.Model):
    """Versículos referenciados no sermão"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sermon = models.ForeignKey(Sermon, on_delete=models.CASCADE, related_name='verses')
    verse = models.ForeignKey('bible.BibleVerse', on_delete=models.CASCADE)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sermon_verses'
        verbose_name = 'Versículo do Sermão'
        verbose_name_plural = 'Versículos dos Sermões'
        ordering = ['order_index']

    def __str__(self):
        return f"{self.sermon.title} - {self.verse.reference}"


class SermonTag(models.Model):
    """Tags para categorização de sermões"""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'sermon_tags'
        verbose_name = 'Tag de Sermão'
        verbose_name_plural = 'Tags de Sermões'

    def __str__(self):
        return self.name


class SermonTagRelation(models.Model):
    """Relacionamento N:N entre Sermões e Tags"""

    sermon = models.ForeignKey(Sermon, on_delete=models.CASCADE, related_name='tag_relations')
    tag = models.ForeignKey(SermonTag, on_delete=models.CASCADE, related_name='sermon_relations')

    class Meta:
        db_table = 'sermon_tag_relations'
        unique_together = ['sermon', 'tag']
        verbose_name = 'Relação Sermão-Tag'
        verbose_name_plural = 'Relações Sermão-Tag'