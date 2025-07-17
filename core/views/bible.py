from rest_framework.response import Response
from rest_framework.decorators import api_view
from collections import defaultdict
from ..services.bible_queries import get_all_verses_of_book, get_chapter_verses, get_verses_by_range

@api_view(['GET'])
def get_verses(request, version, book, chapter, verses):
    """
    Retorna versículos específico da Bíblia indicados no último parametro.

    Parâmetros:
    - version: Abreviação da versão bíblica (ex: 'nvi')
    - book: Abreviação do livro bíblico (ex: 'gn' para Gênesis)
    - chapter: Número do capítulo
    - verses: Número do versículo inicial seguido pelo final separado por um "-" (hífen)

    Retorna:
    - Lista de versículos com id, número, texto, capítulo, livro e versão
    """

    if '-' in verses:
        start, end = map(int, verses.split('-'))
    else:
        start = end = int(verses)

    data = get_verses_by_range(version, book, chapter, start, end)

    if not data:
        return Response({"detail": "Nenhum versículo encontrado."}, status=404)

    # Pega informações únicas do primeiro versículo (pois são iguais em todos)
    first_row = data[0]

    response = {
        "version": first_row["version"],
        "book": {
            "abbreviation": book,
            "name": first_row["book"]
        },
        "chapter": int(chapter),
        "verses": [
            {
                "id": row["verse_id"],
                "number": row["number"],
                "text": row["text"]
            }
            for row in data
        ]
    }

    return Response(response)


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

    if not data:
        return Response({"detail": "Nenhum versículo encontrado."}, status=404)

    # Pega informações únicas do primeiro versículo (pois são iguais em todos)
    first_row = data[0]

    response = {
        "version": first_row["version"],
        "book": {
            "abbreviation": book,
            "name": first_row["book"]
        },
        "chapter": int(chapter),
        "verses": [
            {
                "id": row["verse_id"],
                "number": row["verse_number"],
                "text": row["text"]
            }
            for row in data
        ]
    }

    return Response(response)

