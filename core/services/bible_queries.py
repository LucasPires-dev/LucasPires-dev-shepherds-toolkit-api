from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import connection

@api_view(['GET'])
def get_version_info(request, version):
    # Aqui você pode buscar no banco Supabase ou retornar um exemplo temporário
    dummy_data = {
        "version": version,
        "language": "Português",
        "abbreviation": version,
        "description": "Exemplo de descrição da versão bíblica"
    }
    return Response(dummy_data)

def get_chapter_verses(version, book, chapter):
    """
    Retorna todos os versículos de um capítulo específico.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM verses
            WHERE version = %s AND book = %s AND chapter = %s
            ORDER BY verse_number
        """, [version, book, chapter])
        results = cursor.fetchall()
    return results

def get_verses_by_range(version, book, chapter, start, end):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM verses
            WHERE version = %s AND book = %s AND chapter = %s AND verse_number BETWEEN %s AND %s
        """, [version, book, chapter, start, end])
        results = cursor.fetchall()
    return results