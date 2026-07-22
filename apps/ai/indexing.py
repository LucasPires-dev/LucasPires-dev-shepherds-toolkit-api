from django.conf import settings
from django.db import connection

from .services import _get_client


def _chunk_text(text, size=800):
    """Quebra um texto em pedaços de até `size` caracteres, respeitando
    parágrafos quando possível."""
    paragraphs = [p.strip() for p in (text or '').split('\n') if p.strip()]
    if not paragraphs:
        return []

    chunks = []
    current = ''
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 1 > size:
            chunks.append(current)
            current = paragraph
        else:
            current = f'{current}\n{paragraph}'.strip()
    if current:
        chunks.append(current)
    return chunks


def _generate_embedding(text):
    client = _get_client()
    response = client.embeddings.create(model=settings.AI_EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def reindex_source(user, source_type, instance, text):
    """(Re)gera os EmbeddingChunk de um Escrito/nota/destaque. No-op fora do
    Postgres — em SQLite (dev local) a tabela nem existe."""
    if connection.vendor != 'postgresql':
        return

    from .models import EmbeddingChunk

    field_name = source_type
    EmbeddingChunk.objects.filter(**{field_name: instance}).delete()

    chunks = _chunk_text(text)
    for index, chunk in enumerate(chunks):
        embedding = _generate_embedding(chunk)
        EmbeddingChunk.objects.create(
            user=user,
            source_type=source_type,
            chunk_index=index,
            content=chunk,
            embedding=embedding,
            **{field_name: instance},
        )
