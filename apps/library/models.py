import uuid
from django.db import models


class LibraryResource(models.Model):
    """Recursos da biblioteca teológica"""

    RESOURCE_TYPE_CHOICES = [
        ('book', 'Livro'),
        ('commentary', 'Comentário'),
        ('dictionary', 'Dicionário'),
        ('article', 'Artigo'),
        ('study', 'Estudo'),
        ('other', 'Outro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='library_resources')
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=255, blank=True, null=True)
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPE_CHOICES)
    category = models.CharField(max_length=100, blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    cover_image_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'library_resources'
        verbose_name = 'Recurso da Biblioteca'
        verbose_name_plural = 'Recursos da Biblioteca'
        ordering = ['title']

    def __str__(self):
        return self.title


class LibraryHighlight(models.Model):
    """Marcações em recursos da biblioteca"""

    COLOR_CHOICES = [
        ('yellow', 'Amarelo'),
        ('green', 'Verde'),
        ('blue', 'Azul'),
        ('pink', 'Rosa'),
        ('purple', 'Roxo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='library_highlights')
    resource = models.ForeignKey(LibraryResource, on_delete=models.CASCADE, related_name='highlights')
    page_number = models.IntegerField(blank=True, null=True)
    highlighted_text = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'library_highlights'
        verbose_name = 'Marcação de Biblioteca'
        verbose_name_plural = 'Marcações de Biblioteca'

    def __str__(self):
        return f"{self.resource.title} - Pág. {self.page_number}"

