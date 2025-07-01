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
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT v.id, v.number AS verse_number, v.text,
                   c.number AS chapter_number, b.name AS book_name, ver.name AS version_name
            FROM verses v
            INNER JOIN chapters c ON v.chapter_id = c.id
            INNER JOIN books b ON c.book_id = b.id
            INNER JOIN versions ver ON b.version_id = ver.id
            WHERE ver.name = %s AND b.abbreviation = %s AND c.number = %s
            ORDER BY v.number ASC
        """, [version, book, chapter])
        rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append({
            "verse_id": row[0],
            "verse_number": row[1],
            "text": row[2],
            "chapter": row[3],
            "book": row[4],
            "version": row[5],
        })
    return results



def get_verses_by_range(version, book_abbreviation, chapter_number, start, end):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                v.id AS verse_id,
                v.number,
                v.text,
                c.number AS chapter,
                b.name AS book,
                b.abbreviation AS book_abbr,
                ver.name AS version
            FROM verses v
            JOIN chapters c ON v.chapter_id = c.id
            JOIN books b ON c.book_id = b.id
            JOIN versions ver ON b.version_id = ver.id
            WHERE ver.name = %s
              AND b.abbreviation = %s
              AND c.number = %s
              AND v.number BETWEEN %s AND %s
            ORDER BY v.number
        """, [version, book_abbreviation, chapter_number, start, end])
        
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]




def get_all_verses_of_book(version, book_abbreviation):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                v.id AS verse_id,
                v.verse_number,
                v.text,
                c.chapter_number AS chapter,
                b.name AS book,
                b.abbreviation AS book_abbr,
                ver.abbreviation AS version
            FROM verses v
            JOIN chapters c ON v.chapter_id = c.id
            JOIN books b ON c.book_id = b.id
            JOIN versions ver ON v.version_id = ver.id
            WHERE ver.abbreviation = %s AND b.abbreviation = %s
            ORDER BY c.chapter_number, v.verse_number
        """, [version, book_abbreviation])

        columns = [col[0] for col in cursor.description]
        results = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    return results