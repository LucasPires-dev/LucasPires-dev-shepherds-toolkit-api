from rest_framework.response import Response
from rest_framework.decorators import api_view
from collections import defaultdict
from ..services.bible_queries import get_all_verses_of_book, get_chapter_verses, get_verses_by_range

@api_view(['GET'])
def get_verses(request, version, book, chapter, verses):
    if '-' in verses:
        start, end = map(int, verses.split('-'))
    else:
        start = end = int(verses)

    data = get_verses_by_range(version, book, chapter, start, end)

    # Agora os dados já são dicionários, não precisa mapear de novo
    return Response(data)

from collections import defaultdict

@api_view(['GET'])
def get_book(request, version, book):
    data = get_all_verses_of_book(version, book)

    chapters_dict = defaultdict(list)

    for row in data:
        chapters_dict[row["chapter"]].append({
            "verse_number": row["verse_number"],
            "text": row["text"]
        })

    chapters_list = [
        {
            "chapter": chapter_num,
            "verses": verses
        }
        for chapter_num, verses in sorted(chapters_dict.items())
    ]

    return Response({
        "book": {
            "abbreviation": book,
            "name": data[0]["book"] if data else ""
        },
        "version": version,
        "chapters": chapters_list
    })



@api_view(['GET'])
def get_chapter(request, version, book, chapter):

    """
    Retorna todos os versículos de um capítulo específico da Bíblia.

    Parâmetros:
    - version: Abreviação da versão bíblica (ex: 'nvi')
    - book: Abreviação do livro bíblico (ex: 'gn' para Gênesis)
    - chapter: Número do capítulo

    Retorna:
    - Lista de versículos com id, número, texto, capítulo, livro e versão
    """

    data = get_chapter_verses(version, book, chapter)

    return Response(data)

