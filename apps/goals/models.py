import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Goal(models.Model):
    """Metas e objetivos ministeriais"""

    CATEGORY_CHOICES = [
        ('church', 'Igreja'),
        ('ministry', 'Ministério'),
        ('personal', 'Pessoal'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
    ]

    STATUS_CHOICES = [
        ('not_started', 'Não Iniciada'),
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluída'),
        ('paused', 'Pausada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    ministry_type = models.CharField(max_length=100, blank=True, null=True,
                                     help_text="Ex: louvor, jovens, crianças")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='not_started')
    progress_percentage = models.IntegerField(default=0,
                                              validators=[MinValueValidator(0),
                                                          MaxValueValidator(100)])
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'goals'
        verbose_name = 'Meta'
        verbose_name_plural = 'Metas'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class GoalTask(models.Model):
    """Tarefas/Etapas das metas"""

    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluída'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    responsible = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    order_index = models.IntegerField(default=0)
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'goal_tasks'
        verbose_name = 'Tarefa da Meta'
        verbose_name_plural = 'Tarefas das Metas'
        ordering = ['order_index']

    def __str__(self):
        return f"{self.goal.title} - {self.title}"


class GoalComment(models.Model):
    """Comentários e atualizações nas metas"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'goal_comments'
        verbose_name = 'Comentário da Meta'
        verbose_name_plural = 'Comentários das Metas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.goal.title} - {self.user.username}"

