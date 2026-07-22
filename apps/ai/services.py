import re

from django.conf import settings
from django.db import connection
from django.db.models import Q, Sum
from django.utils import timezone
from openai import OpenAI

from .models import AIInteraction, AIQuota

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


class QuotaExceededError(Exception):
    def __init__(self, plan, limit, used, reset_at):
        self.plan = plan
        self.limit = limit
        self.used = used
        self.reset_at = reset_at
        super().__init__(f"Cota de IA excedida para o plano '{plan}'")


class AIServiceError(Exception):
    """Erro ao chamar o provedor de IA (timeout, rate limit da OpenAI, etc)."""


def _current_period_start():
    now = timezone.now()
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _next_period_start(period_start):
    if period_start.month == 12:
        return period_start.replace(year=period_start.year + 1, month=1)
    return period_start.replace(month=period_start.month + 1)


def get_usage_summary(user):
    """Uso do mês corrente do usuário, calculado por agregação (sem contador/Celery)."""
    quota, _ = AIQuota.objects.get_or_create(user=user)
    limit = settings.AI_PLAN_LIMITS.get(quota.plan, settings.AI_PLAN_LIMITS['free'])['monthly_tokens']

    period_start = _current_period_start()
    used = AIInteraction.objects.filter(
        user=user, created_at__gte=period_start
    ).aggregate(total=Sum('total_tokens'))['total'] or 0

    return {
        'plan': quota.plan,
        'monthly_token_limit': limit,
        'tokens_used': used,
        'tokens_remaining': None if limit is None else max(limit - used, 0),
        'period_reset_at': _next_period_start(period_start),
    }


def _check_quota(user):
    usage = get_usage_summary(user)
    limit = usage['monthly_token_limit']
    if limit is not None and usage['tokens_used'] >= limit:
        raise QuotaExceededError(usage['plan'], limit, usage['tokens_used'], usage['period_reset_at'])
    return usage


_SYSTEM_PROMPTS = {
    'context': 'Você é um assistente teológico. Explique o contexto histórico e literário do texto bíblico informado, de forma objetiva.',
    'etymology': 'Você é um assistente teológico. Explique a etimologia dos termos originais (hebraico/grego) relevantes do texto informado.',
    'related_texts': 'Você é um assistente teológico. Sugira textos bíblicos relacionados ao tema ou passagem informada, com breve justificativa.',
    'application': 'Você é um assistente pastoral. Sugira aplicações práticas e contemporâneas para o texto bíblico informado.',
}

# Stopwords curtas em português — só o suficiente pra não deixar preposições/
# pronomes comuns virarem termo de busca no conteúdo pessoal do usuário.
_STOPWORDS_PT = {
    'de', 'da', 'do', 'das', 'dos', 'para', 'com', 'que', 'uma', 'um', 'uns', 'umas',
    'como', 'sobre', 'este', 'esta', 'esse', 'essa', 'isso', 'isto', 'aquele', 'aquela',
    'qual', 'quais', 'onde', 'quando', 'porque', 'por', 'sem', 'seu', 'sua', 'seus', 'suas',
    'meu', 'minha', 'meus', 'minhas', 'nos', 'nas', 'pelo', 'pela', 'pelos', 'pelas',
    'mais', 'menos', 'muito', 'muita', 'muitos', 'muitas', 'pode', 'poderia',
    'explique', 'explicar', 'sugira', 'sugerir', 'texto', 'textos',
}

_WORD_RE = re.compile(r'[a-zà-ÿ]{4,}', re.IGNORECASE)


def _extract_keywords(text, limit=6):
    words = _WORD_RE.findall(text.lower())
    keywords = []
    for word in words:
        if word in _STOPWORDS_PT or word in keywords:
            continue
        keywords.append(word)
        if len(keywords) >= limit:
            break
    return keywords


def _truncate(text, length=250):
    text = (text or '').strip()
    return text if len(text) <= length else text[:length].rsplit(' ', 1)[0] + '…'


def _build_favorites_line(user):
    """Versículos favoritados do usuário — sinal fixo, independe de keyword
    match ou de busca semântica. Reaproveitado pelos dois caminhos abaixo."""
    from apps.bible.models import VerseHighlight

    favorites = VerseHighlight.objects.filter(user=user, is_favorite=True).select_related('verse__book').order_by('-created_at')[:5]
    if not favorites:
        return ''
    refs = ', '.join(f.verse.reference for f in favorites)
    return f'- Versículos que o usuário marcou como favoritos: {refs}'


def _build_user_context(user, query):
    """Busca por palavra-chave no conteúdo pessoal do usuário (escritos,
    anotações em versículos, destaques de biblioteca) e monta um bloco curto
    de contexto pra enriquecer a resposta da IA. Fase 1 — busca literal
    (icontains). Usado como fallback quando a busca semântica (Fase 2, só em
    Postgres) não está disponível."""
    from apps.bible.models import VerseNote
    from apps.library.models import LibraryHighlight
    from apps.writings.models import Writing

    keywords = _extract_keywords(query)
    if not keywords:
        return ''

    lines = []
    budget = 1500

    def add_line(line):
        nonlocal budget
        if budget <= 0:
            return
        lines.append(line)
        budget -= len(line)

    writing_q = Q()
    note_q = Q()
    library_q = Q()
    for kw in keywords:
        writing_q |= Q(title__icontains=kw) | Q(content__icontains=kw) | Q(theme__icontains=kw)
        note_q |= Q(note__icontains=kw)
        library_q |= Q(highlighted_text__icontains=kw) | Q(note__icontains=kw)

    writings = Writing.objects.filter(user=user).filter(writing_q).order_by('-updated_at')[:3]
    for w in writings:
        add_line(f'- [Escrito "{w.title}"]: {_truncate(w.content)}')

    notes = VerseNote.objects.filter(user=user).filter(note_q).select_related('verse__book').order_by('-updated_at')[:3]
    for n in notes:
        add_line(f'- [Nota em {n.verse.reference}]: {_truncate(n.note)}')

    highlights = LibraryHighlight.objects.filter(user=user).filter(library_q).select_related('resource').order_by('-created_at')[:3]
    for h in highlights:
        add_line(f'- [Biblioteca "{h.resource.title}"]: {_truncate(h.note or h.highlighted_text)}')

    return '\n'.join(lines)


_SOURCE_LABELS = {
    'writing': 'Escrito',
    'verse_note': 'Nota',
    'library_highlight': 'Biblioteca',
}


def _build_semantic_context(user, query):
    """Busca semântica (Fase 2) via pgvector — retorna None fora do Postgres,
    sinal pra quem chamar usar o fallback por palavra-chave (_build_user_context)."""
    if connection.vendor != 'postgresql':
        return None

    from pgvector.django import CosineDistance

    from .indexing import _generate_embedding
    from .models import EmbeddingChunk

    query_embedding = _generate_embedding(query)
    chunks = (
        EmbeddingChunk.objects.filter(user=user)
        .annotate(distance=CosineDistance('embedding', query_embedding))
        .order_by('distance')[:5]
    )

    lines = []
    budget = 1500
    for chunk in chunks:
        if budget <= 0:
            break
        label = _SOURCE_LABELS.get(chunk.source_type, chunk.source_type)
        line = f'- [{label}]: {_truncate(chunk.content, 300)}'
        lines.append(line)
        budget -= len(line)

    return '\n'.join(lines)


def run_ai_completion(user, interaction_type, query, verse=None):
    """Executa uma chamada de IA em nome do usuário, respeitando a cota mensal
    dele. Levanta QuotaExceededError se a cota estourou (nada é debitado nesse
    caso) e AIServiceError se a OpenAI falhar (também nada é debitado)."""
    _check_quota(user)

    client = _get_client()
    system_prompt = _SYSTEM_PROMPTS.get(interaction_type, _SYSTEM_PROMPTS['context'])

    messages = [{'role': 'system', 'content': system_prompt}]

    semantic_context = _build_semantic_context(user, query)
    user_context = semantic_context if semantic_context is not None else _build_user_context(user, query)
    favorites_line = _build_favorites_line(user)
    if favorites_line:
        user_context = f'{user_context}\n{favorites_line}'.strip()

    if user_context:
        messages.append({
            'role': 'system',
            'content': (
                'Contexto pessoal do usuário — use apenas se for relevante para a '
                'pergunta, e diga explicitamente quando estiver se baseando nisso '
                '(ex: "isso conecta com o que você escreveu em..."). Não invente '
                'conteúdo além do que está aqui:\n' + user_context
            ),
        })
    messages.append({'role': 'user', 'content': query})

    try:
        completion = client.chat.completions.create(
            model=settings.AI_DEFAULT_MODEL,
            max_tokens=settings.AI_MAX_TOKENS_PER_REQUEST,
            messages=messages,
        )
    except Exception as exc:
        raise AIServiceError(str(exc)) from exc

    answer = completion.choices[0].message.content or ''
    usage = completion.usage

    interaction = AIInteraction.objects.create(
        user=user,
        verse=verse,
        interaction_type=interaction_type,
        query=query,
        response=answer,
        model=completion.model,
        prompt_tokens=usage.prompt_tokens if usage else 0,
        completion_tokens=usage.completion_tokens if usage else 0,
        total_tokens=usage.total_tokens if usage else 0,
    )
    return interaction
