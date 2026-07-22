import re

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.bible.models import VerseNote
from apps.library.models import LibraryHighlight
from apps.writings.models import Writing

from .indexing import reindex_source
from .models import AIQuota


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_ai_quota(sender, instance, created, **kwargs):
    """Provisiona a cota de IA do usuário automaticamente na criação da conta."""
    if created:
        AIQuota.objects.get_or_create(user=instance)


def _strip_html(html):
    return re.sub(r'<[^>]+>', ' ', html or '')


@receiver(post_save, sender=Writing)
def index_writing(sender, instance, **kwargs):
    reindex_source(instance.user, 'writing', instance, _strip_html(instance.content))


@receiver(post_save, sender=VerseNote)
def index_verse_note(sender, instance, **kwargs):
    reindex_source(instance.user, 'verse_note', instance, instance.note)


@receiver(post_save, sender=LibraryHighlight)
def index_library_highlight(sender, instance, **kwargs):
    text = f'{instance.highlighted_text or ""}\n{instance.note or ""}'.strip()
    reindex_source(instance.user, 'library_highlight', instance, text)
