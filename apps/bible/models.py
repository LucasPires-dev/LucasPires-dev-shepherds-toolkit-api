import uuid
from django.db import models

class BibleBook(models.Model):
    """Livros da Bíblia"""

    TESTAMENT_CHOICES = [
        ('old', 'Antigo Testamento'),
        ('new', 'Novo Testamento'),
    ]

    name = models.CharField(max_length=100)
    abbrev = models.CharField(max_length=10)
    testament = models.CharField(max_length=20, choices=TESTAMENT_CHOICES)
    book_order = models.IntegerField()
    total_chapters = models.IntegerField()

    class Meta:
        db_table = 'bible_books'
        verbose_name = 'Livro da Bíblia'
        verbose_name_plural = 'Livros da Bíblia'
        ordering = ['book_order']

    def __str__(self):
        return self.name


class BibleVerse(models.Model):
    """Versículos da Bíblia"""

    VERSION_CHOICES = [
        ('ACF', 'Almeida Corrigida Fiel'),
        ('ARA', 'Almeida Revista e Atualizada'),
        ('NVI', 'Nova Versão Internacional'),
        ('NTLH', 'Nova Tradução na Linguagem de Hoje'),
        ('NAA', 'Nova Almeida Atualizada'),
        ('KJV', 'King James Version'),
    ]

    book = models.ForeignKey(BibleBook, on_delete=models.CASCADE, related_name='verses')
    chapter = models.IntegerField()
    verse = models.IntegerField()
    text = models.TextField()
    version = models.CharField(max_length=10, choices=VERSION_CHOICES, default='ACF')

    class Meta:
        db_table = 'bible_verses'
        verbose_name = 'Versículo'
        verbose_name_plural = 'Versículos'
        unique_together = ['book', 'chapter', 'verse', 'version']
        ordering = ['book__book_order', 'chapter', 'verse']

    def __str__(self):
        return f"{self.book.name} {self.chapter}:{self.verse}"

    @property
    def reference(self):
        return f"{self.book.name} {self.chapter}:{self.verse}"


class VerseHighlight(models.Model):
    """Marcações de versículos pelos usuários"""

    COLOR_CHOICES = [
        ('yellow', 'Amarelo'),
        ('green', 'Verde'),
        ('blue', 'Azul'),
        ('pink', 'Rosa'),
        ('purple', 'Roxo'),
        ('', "Nenhum")
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='verse_highlights')
    verse = models.ForeignKey(BibleVerse, on_delete=models.CASCADE, related_name='highlights')
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, blank=True, null=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ← ADICIONE ESTA LINHA

    class Meta:
        db_table = 'verse_highlights'
        verbose_name = 'Marcação de Versículo'
        verbose_name_plural = 'Marcações de Versículos'
        unique_together = ['user', 'verse']  # ← ADICIONE ESTA LINHA

    def __str__(self):
        return f"{self.user.username} - {self.verse.reference}"


class VerseNote(models.Model):
    """Anotações em versículos"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='verse_notes')
    verse = models.ForeignKey(BibleVerse, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'verse_notes'
        verbose_name = 'Anotação de Versículo'
        verbose_name_plural = 'Anotações de Versículos'

    def __str__(self):
        return f"{self.user.username} - {self.verse.reference}"


class ReadingPlan(models.Model):
    """Planos de leitura bíblica"""

    PLAN_TYPE_CHOICES = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('custom', 'Personalizado'),
    ]

    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('completed', 'Concluído'),
        ('paused', 'Pausado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reading_plans')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    plan_type = models.CharField(max_length=50, choices=PLAN_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reading_plans'
        verbose_name = 'Plano de Leitura'
        verbose_name_plural = 'Planos de Leitura'

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class ReadingPlanProgress(models.Model):
    """Progresso do plano de leitura"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(ReadingPlan, on_delete=models.CASCADE, related_name='progress')
    book = models.ForeignKey(BibleBook, on_delete=models.CASCADE)
    chapter = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'reading_plan_progress'
        verbose_name = 'Progresso de Leitura'
        verbose_name_plural = 'Progressos de Leitura'

    def __str__(self):
        return f"{self.plan.name} - {self.book.name} {self.chapter}"

