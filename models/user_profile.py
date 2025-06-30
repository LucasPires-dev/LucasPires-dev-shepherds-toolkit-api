from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('pastor', 'Pastor'),
        ('leader', 'Líder'),
        ('member', 'Membro'),
    ]

    THEME_CHOICES = [
        ('light', 'Claro'),
        ('dark', 'Escuro'),
    ]

    LANGUAGE_CHOICES = [
        ('pt-br', 'Português (Brasil)'),
        ('en', 'English'),
        ('es', 'Español'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    church_name = models.CharField(max_length=255, blank=True)
    church_location = models.CharField(max_length=255, blank=True)
    ordination_date = models.DateField(null=True, blank=True)
    ministerial_focus = models.CharField(max_length=100, blank=True)

    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='pt-br')

    verse_version_default = models.CharField(max_length=20, default='nvi')  # ou use ForeignKey se tiver model Version

    created_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.display_name or self.user.username
    
    class Meta:
        app_label = 'core'
