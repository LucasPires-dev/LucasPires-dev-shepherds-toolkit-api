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
        ('ALM1911', 'Almeida 1911 (Domínio Público)'),
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


# Adicione estes modelos ao arquivo apps/bible/models.py existente

class ReadingPlanTemplate(models.Model):
    """Templates de planos de leitura predefinidos"""

    PLAN_TYPE_CHOICES = [
        ('bible_year', 'Bíblia em 1 Ano'),
        ('nt_90days', 'Novo Testamento em 90 Dias'),
        ('psalms_month', 'Salmos em 1 Mês'),
        ('custom', 'Personalizado'),
    ]

    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    plan_type = models.CharField(max_length=50, choices=PLAN_TYPE_CHOICES)
    duration_days = models.IntegerField()
    icon = models.CharField(max_length=10, default='📖')
    color = models.CharField(max_length=50, default='from-blue-500 to-blue-600')
    readings_count = models.IntegerField()
    readings_data = models.JSONField(default=list)  # Lista de leituras diárias
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reading_plan_templates'
        verbose_name = 'Template de Plano'
        verbose_name_plural = 'Templates de Planos'

    def __str__(self):
        return self.name


class UserReadingPlan(models.Model):
    """Planos de leitura dos usuários"""

    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('completed', 'Concluído'),
        ('paused', 'Pausado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_reading_plans')
    template = models.ForeignKey(ReadingPlanTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    plan_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_reading_plans'
        verbose_name = 'Plano de Leitura do Usuário'
        verbose_name_plural = 'Planos de Leitura dos Usuários'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    @property
    def days_completed(self):
        return self.reading_days.filter(status='completed').count()

    @property
    def progress_percentage(self):
        if self.total_days == 0:
            return 0
        return round((self.days_completed / self.total_days) * 100, 1)


class ReadingDay(models.Model):
    """Dias de leitura individuais"""

    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('completed', 'Concluída'),
        ('skipped', 'Pulada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(UserReadingPlan, on_delete=models.CASCADE, related_name='reading_days')
    date = models.DateField()
    day_number = models.IntegerField()
    readings_data = models.JSONField()  # Lista de referências bíblicas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reading_days'
        verbose_name = 'Dia de Leitura'
        verbose_name_plural = 'Dias de Leitura'
        ordering = ['date']
        unique_together = ['plan', 'date']

    def __str__(self):
        return f"{self.plan.name} - Dia {self.day_number}"