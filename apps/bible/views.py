import re
import requests
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.core.cache import cache
from .models import (
    BibleBook, BibleVerse, VerseHighlight, VerseNote,
    ReadingPlan, ReadingPlanProgress
)
from .serializers import (
    BibleBookSerializer, BibleVerseSerializer, VerseHighlightSerializer,
    VerseNoteSerializer, ReadingPlanSerializer, ReadingPlanProgressSerializer
)
from .reference_parser import parse_reference, format_reference
from django.db.models import Prefetch


def _truncate(text, length):
    text = text.strip()
    return text if len(text) <= length else text[:length].rsplit(' ', 1)[0] + '…'


# Códigos USX (padrão da api.bible / USFM) na mesma ordem canônica dos 66
# livros já cadastrados via book_order — permite mapear book_order -> código
# sem depender de abreviações, que variam de fonte para fonte.
USX_BOOK_CODES = [
    'GEN', 'EXO', 'LEV', 'NUM', 'DEU', 'JOS', 'JDG', 'RUT', '1SA', '2SA',
    '1KI', '2KI', '1CH', '2CH', 'EZR', 'NEH', 'EST', 'JOB', 'PSA', 'PRO',
    'ECC', 'SNG', 'ISA', 'JER', 'LAM', 'EZK', 'DAN', 'HOS', 'JOL', 'AMO',
    'OBA', 'JON', 'MIC', 'NAM', 'HAB', 'ZEP', 'HAG', 'ZEC', 'MAL',
    'MAT', 'MRK', 'LUK', 'JHN', 'ACT', 'ROM', '1CO', '2CO', 'GAL', 'EPH',
    'PHP', 'COL', '1TH', '2TH', '1TI', '2TI', 'TIT', 'PHM', 'HEB', 'JAS',
    '1PE', '2PE', '1JN', '2JN', '3JN', 'JUD', 'REV',
]

_VERSE_SPAN_RE = re.compile(r'<span[^>]*data-number="(\d+)"[^>]*class="v">.*?</span>', re.DOTALL)
_TAG_RE = re.compile(r'<[^>]+>')


def _parse_api_bible_chapter_html(html):
    """Divide o HTML de um capítulo da api.bible em {numero_versiculo: texto}."""
    markers = list(_VERSE_SPAN_RE.finditer(html))
    verses = {}
    for i, m in enumerate(markers):
        number = int(m.group(1))
        start = m.end()
        end = markers[i + 1].start() if i + 1 < len(markers) else len(html)
        raw = html[start:end]
        text = _TAG_RE.sub(' ', raw)
        text = text.replace('¶', ' ')
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            verses[number] = text
    return verses


def _fetch_external_chapter(external_bible_id, usx_code, chapter):
    """Busca um capítulo na api.bible, com cache curto (não guardamos o texto
    permanentemente — cf. termos de uso da api.bible)."""
    cache_key = f'api_bible:{external_bible_id}:{usx_code}.{chapter}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    if not settings.API_BIBLE_KEY:
        return None

    url = f'https://api.scripture.api.bible/v1/bibles/{external_bible_id}/chapters/{usx_code}.{chapter}'
    try:
        response = requests.get(
            url,
            headers={'api-key': settings.API_BIBLE_KEY},
            params={'content-type': 'html', 'include-verse-numbers': 'true'},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    data = response.json().get('data', {})
    verses = _parse_api_bible_chapter_html(data.get('content', ''))
    result = {'verses': verses, 'copyright': data.get('copyright', '')}
    cache.set(cache_key, result, timeout=60 * 60)  # 1h, bem dentro do limite de 30 dias deles
    return result


class BibleBookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BibleBook.objects.all()
    serializer_class = BibleBookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['testament']
    search_fields = ['name', 'abbrev']


class BibleVerseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BibleVerseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['book', 'chapter', 'version']
    search_fields = ['text']

    def get_queryset(self):
        queryset = BibleVerse.objects.select_related('book')

        if self.request.user.is_authenticated:
            from django.db.models import Prefetch
            from .models import VerseHighlight
            highlights = VerseHighlight.objects.filter(user=self.request.user)
            queryset = queryset.prefetch_related(
                Prefetch('highlights', queryset=highlights)
            )

        return queryset

    def list(self, request, *args, **kwargs):
        """
        ✅ MODIFICADO: Adiciona navegação de capítulos na resposta
        """
        version = request.query_params.get('version', 'ALM1911')
        external_id = settings.EXTERNAL_BIBLE_IDS.get(version)
        if external_id:
            return self._list_external(request, external_id, version)

        response = super().list(request, *args, **kwargs)

        # Verificar se está buscando um capítulo específico
        # (o frontend envia o id numérico do livro, não a abreviação)
        book_id = request.query_params.get('book')
        chapter = request.query_params.get('chapter')

        if book_id and chapter:
            try:
                chapter = int(chapter)
                book = BibleBook.objects.get(pk=int(book_id))

                # Adicionar navegação à resposta
                navigation = self._get_chapter_navigation(book, chapter, version)
                response.data['chapter_navigation'] = navigation

            except (BibleBook.DoesNotExist, ValueError):
                pass

        return response

    def _list_external(self, request, external_id, version):
        """Serve versículos de uma Bíblia com copyright (ex: NIV) ao vivo pela
        api.bible, no mesmo formato de resposta da lista local — sem persistir
        o texto no nosso banco (conforme os termos de uso da api.bible)."""
        book_param = request.query_params.get('book')
        chapter_param = request.query_params.get('chapter')

        if not book_param or not chapter_param:
            return Response({'detail': 'Parâmetros "book" e "chapter" são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = BibleBook.objects.get(pk=int(book_param))
            chapter = int(chapter_param)
        except (BibleBook.DoesNotExist, ValueError):
            return Response({'detail': 'Livro ou capítulo inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if book.book_order < 1 or book.book_order > len(USX_BOOK_CODES):
            return Response({'detail': 'Livro fora do intervalo suportado.'}, status=status.HTTP_400_BAD_REQUEST)

        usx_code = USX_BOOK_CODES[book.book_order - 1]
        chapter_data = _fetch_external_chapter(external_id, usx_code, chapter)

        if chapter_data is None:
            return Response({'detail': 'Não foi possível obter o texto dessa versão agora. Tente novamente em instantes.'}, status=status.HTTP_502_BAD_GATEWAY)

        results = []
        for verse_number in sorted(chapter_data['verses']):
            results.append({
                'id': f'{version}-{book.id}-{chapter}-{verse_number}',
                'book': book.id,
                'book_name': book.name,
                'chapter': chapter,
                'verse': verse_number,
                'text': chapter_data['verses'][verse_number],
                'version': version,
                'reference': f'{book.name} {chapter}:{verse_number}',
                'user_highlight': None,
                'navigation': None,
                'copyright': chapter_data['copyright'],
            })

        navigation = self._get_chapter_navigation(book, chapter, version)

        return Response({
            'count': len(results),
            'next': None,
            'previous': None,
            'results': results,
            'chapter_navigation': navigation,
        })

    def _get_chapter_navigation(self, book, chapter, version):
        """Gera informações de navegação entre capítulos"""

        # Buscar livros anterior e próximo
        previous_book = BibleBook.objects.filter(
            book_order=book.book_order - 1
        ).first()

        next_book = BibleBook.objects.filter(
            book_order=book.book_order + 1
        ).first()

        navigation = {
            'current': {
                'book': book.abbrev,
                'book_name': book.name,
                'chapter': chapter,
                'total_chapters': book.total_chapters,
                'testament': book.testament
            },
            'previous': None,
            'next': None,
            'book_chapters': {
                'first': 1,
                'last': book.total_chapters,
                'current': chapter
            }
        }

        # Capítulo anterior
        if chapter > 1:
            navigation['previous'] = {
                'book': book.abbrev,
                'book_name': book.name,
                'chapter': chapter - 1,
                'is_same_book': True,
                'url': f'/api/bible/verses/?book={book.abbrev}&chapter={chapter - 1}&version={version}'
            }
        elif previous_book:
            navigation['previous'] = {
                'book': previous_book.abbrev,
                'book_name': previous_book.name,
                'chapter': previous_book.total_chapters,
                'is_same_book': False,
                'url': f'/api/bible/verses/?book={previous_book.abbrev}&chapter={previous_book.total_chapters}&version={version}'
            }

        # Próximo capítulo
        if chapter < book.total_chapters:
            navigation['next'] = {
                'book': book.abbrev,
                'book_name': book.name,
                'chapter': chapter + 1,
                'is_same_book': True,
                'url': f'/api/bible/verses/?book={book.abbrev}&chapter={chapter + 1}&version={version}'
            }
        elif next_book:
            navigation['next'] = {
                'book': next_book.abbrev,
                'book_name': next_book.name,
                'chapter': 1,
                'is_same_book': False,
                'url': f'/api/bible/verses/?book={next_book.abbrev}&chapter=1&version={version}'
            }

        return navigation

    @action(detail=False, methods=['get'])
    def by_reference(self, request):
        """Busca versículos por referência solta em pt-BR (ex: 'jo 3:16', 'salmos 23').

        Usado pelo autocomplete de citação bíblica do editor de sermões.
        Como o nome do livro pode ser ambíguo (ex: 'cor' -> 1 ou 2 Coríntios),
        retorna um candidato por livro compatível, não só o primeiro achado.
        """
        query = request.query_params.get('q', '').strip()
        version = request.query_params.get('version', 'ALM1911')

        if not query:
            return Response({'query': query, 'results': []})

        parsed = parse_reference(query)
        if not parsed:
            return Response({'query': query, 'results': []})

        results = []
        for abbrev in parsed.book_abbrevs:
            book = BibleBook.objects.filter(abbrev=abbrev).first()
            if not book or parsed.chapter > book.total_chapters:
                continue

            chapter_verses = BibleVerse.objects.filter(
                book=book, chapter=parsed.chapter, version=version
            ).order_by('verse')

            if parsed.verse_start:
                verses = list(chapter_verses.filter(
                    verse__gte=parsed.verse_start, verse__lte=parsed.verse_end
                ))
                if not verses:
                    continue
                text = ' '.join(v.text for v in verses)
                results.append({
                    'book_abbrev': book.abbrev,
                    'book_name': book.name,
                    'chapter': parsed.chapter,
                    'verse_start': parsed.verse_start,
                    'verse_end': parsed.verse_end,
                    'reference': format_reference(book.name, parsed.chapter, parsed.verse_start, parsed.verse_end),
                    'version': version,
                    'preview': _truncate(text, 90),
                    'text': text,
                    'verse_ids': [v.id for v in verses],
                })
            else:
                first_verse = chapter_verses.first()
                if not first_verse:
                    continue
                total_verses = chapter_verses.count()
                results.append({
                    'book_abbrev': book.abbrev,
                    'book_name': book.name,
                    'chapter': parsed.chapter,
                    'verse_start': 1,
                    'verse_end': total_verses,
                    'reference': format_reference(book.name, parsed.chapter, None, None),
                    'version': version,
                    'preview': _truncate(first_verse.text, 90),
                    'text': None,
                    'verse_ids': None,
                    'verse_count': total_verses,
                })

        return Response({'query': query, 'results': results[:8]})

class VerseHighlightViewSet(viewsets.ModelViewSet):
    serializer_class = VerseHighlightSerializer

    def get_queryset(self):
        return VerseHighlight.objects.filter(user=self.request.user).select_related('verse', 'verse__book')

    def create(self, request, *args, **kwargs):
        """
        Sobrescreve o create para usar update_or_create.
        Se já existe marcação, atualiza. Se não existe, cria.
        """
        verse_id = request.data.get('verse')

        # Busca ou cria a marcação
        highlight, created = VerseHighlight.objects.update_or_create(
            user=request.user,
            verse_id=verse_id,
            defaults={
                'color': request.data.get('color'),
                'is_favorite': request.data.get('is_favorite', False)
            }
        )

        serializer = self.get_serializer(highlight)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK

        return Response(serializer.data, status=status_code)

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """Lista apenas versículos favoritados"""
        favorites = self.get_queryset().filter(is_favorite=True)
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)


class VerseNoteViewSet(viewsets.ModelViewSet):
    serializer_class = VerseNoteSerializer

    def get_queryset(self):
        return VerseNote.objects.filter(user=self.request.user).select_related('verse', 'verse__book')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReadingPlanViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingPlanSerializer

    def get_queryset(self):
        return ReadingPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_chapter_complete(self, request, pk=None):
        """Marca um capítulo como completo no plano"""
        plan = self.get_object()
        book_id = request.data.get('book_id')
        chapter = request.data.get('chapter')

        progress, created = ReadingPlanProgress.objects.get_or_create(
            plan=plan,
            book_id=book_id,
            chapter=chapter
        )
        progress.is_completed = True
        progress.save()

        return Response({'status': 'completed'})