import uuid
from django.db import models


class Member(models.Model):
    """Membros da igreja"""

    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('visitor', 'Visitante'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='members')
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    member_since = models.DateField(blank=True, null=True)
    baptism_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    ministry = models.CharField(max_length=100, blank=True, null=True)
    cell_group = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'members'
        verbose_name = 'Membro'
        verbose_name_plural = 'Membros'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class PastoralVisit(models.Model):
    """Registro de visitas pastorais"""

    VISIT_TYPE_CHOICES = [
        ('routine', 'Rotina'),
        ('hospital', 'Hospital'),
        ('counseling', 'Aconselhamento'),
        ('emergency', 'Emergência'),
        ('other', 'Outro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='pastoral_visits')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='visits')
    visit_date = models.DateField()
    visit_type = models.CharField(max_length=100, choices=VISIT_TYPE_CHOICES)
    notes = models.TextField(blank=True, null=True)
    follow_up_needed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pastoral_visits'
        verbose_name = 'Visita Pastoral'
        verbose_name_plural = 'Visitas Pastorais'
        ordering = ['-visit_date']

    def __str__(self):
        return f"{self.member.full_name} - {self.visit_date}"

