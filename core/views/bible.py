from rest_framework.response import Response
from rest_framework.decorators import api_view
from core.services.bible_queries import get_chapter_verses, get_verses_by_range

@api_view(['GET'])
def get_verses(request, version, book, chapter, verses):
    if '-' in verses:
        start, end = map(int, verses.split('-'))
    else:
        start = end = int(verses)

    data = get_verses_by_range(version, book, chapter, start, end)
    
    # Mapeie os resultados se necessário
    verses_list = [
        {
            "id": row[0],
            "version": row[1],
            "book": row[2],
            "chapter": row[3],
            "verse_number": row[4],
            "text": row[5]
        }
        for row in data
    ]
    
    return Response(verses_list)


@api_view(['GET'])
def get_chapter(request, version, book, chapter):
    data = get_chapter_verses(version, book, chapter)

    verses = [
        {
            "id": row[0],
            "version": row[1],
            "book": row[2],
            "chapter": row[3],
            "verse_number": row[4],
            "text": row[5]
        }
        for row in data
    ]
    
    return Response(verses)