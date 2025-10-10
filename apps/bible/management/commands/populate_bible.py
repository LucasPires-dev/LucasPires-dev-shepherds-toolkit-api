from django.core.management.base import BaseCommand
from app.bible.models import BibleBook
import json


class Command(BaseCommand):
    help = 'Popula o banco de dados com os livros e versículos da Bíblia'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando população da Bíblia...')

        books_data = [
            # Antigo Testamento
            {'name': 'Gênesis', 'abbrev': 'Gn', 'testament': 'old', 'book_order': 1, 'total_chapters': 50},
            {'name': 'Êxodo', 'abbrev': 'Ex', 'testament': 'old', 'book_order': 2, 'total_chapters': 40},
            {'name': 'Levítico', 'abbrev': 'Lv', 'testament': 'old', 'book_order': 3, 'total_chapters': 27},
            {'name': 'Números', 'abbrev': 'Nm', 'testament': 'old', 'book_order': 4, 'total_chapters': 36},
            {'name': 'Deuteronômio', 'abbrev': 'Dt', 'testament': 'old', 'book_order': 5, 'total_chapters': 34},
            {'name': 'Josué', 'abbrev': 'Js', 'testament': 'old', 'book_order': 6, 'total_chapters': 24},
            {'name': 'Juízes', 'abbrev': 'Jz', 'testament': 'old', 'book_order': 7, 'total_chapters': 21},
            {'name': 'Rute', 'abbrev': 'Rt', 'testament': 'old', 'book_order': 8, 'total_chapters': 4},
            {'name': '1 Samuel', 'abbrev': '1Sm', 'testament': 'old', 'book_order': 9, 'total_chapters': 31},
            {'name': '2 Samuel', 'abbrev': '2Sm', 'testament': 'old', 'book_order': 10, 'total_chapters': 24},
            {'name': '1 Reis', 'abbrev': '1Rs', 'testament': 'old', 'book_order': 11, 'total_chapters': 22},
            {'name': '2 Reis', 'abbrev': '2Rs', 'testament': 'old', 'book_order': 12, 'total_chapters': 25},
            {'name': '1 Crônicas', 'abbrev': '1Cr', 'testament': 'old', 'book_order': 13, 'total_chapters': 29},
            {'name': '2 Crônicas', 'abbrev': '2Cr', 'testament': 'old', 'book_order': 14, 'total_chapters': 36},
            {'name': 'Esdras', 'abbrev': 'Ed', 'testament': 'old', 'book_order': 15, 'total_chapters': 10},
            {'name': 'Neemias', 'abbrev': 'Ne', 'testament': 'old', 'book_order': 16, 'total_chapters': 13},
            {'name': 'Ester', 'abbrev': 'Et', 'testament': 'old', 'book_order': 17, 'total_chapters': 10},
            {'name': 'Jó', 'abbrev': 'Jó', 'testament': 'old', 'book_order': 18, 'total_chapters': 42},
            {'name': 'Salmos', 'abbrev': 'Sl', 'testament': 'old', 'book_order': 19, 'total_chapters': 150},
            {'name': 'Provérbios', 'abbrev': 'Pv', 'testament': 'old', 'book_order': 20, 'total_chapters': 31},
            {'name': 'Eclesiastes', 'abbrev': 'Ec', 'testament': 'old', 'book_order': 21, 'total_chapters': 12},
            {'name': 'Cantares de Salomão', 'abbrev': 'Ct', 'testament': 'old', 'book_order': 22, 'total_chapters': 8},
            {'name': 'Isaías', 'abbrev': 'Is', 'testament': 'old', 'book_order': 23, 'total_chapters': 66},
            {'name': 'Jeremias', 'abbrev': 'Jr', 'testament': 'old', 'book_order': 24, 'total_chapters': 52},
            {'name': 'Lamentações', 'abbrev': 'Lm', 'testament': 'old', 'book_order': 25, 'total_chapters': 5},
            {'name': 'Ezequiel', 'abbrev': 'Ez', 'testament': 'old', 'book_order': 26, 'total_chapters': 48},
            {'name': 'Daniel', 'abbrev': 'Dn', 'testament': 'old', 'book_order': 27, 'total_chapters': 12},
            {'name': 'Oséias', 'abbrev': 'Os', 'testament': 'old', 'book_order': 28, 'total_chapters': 14},
            {'name': 'Joel', 'abbrev': 'Jl', 'testament': 'old', 'book_order': 29, 'total_chapters': 3},
            {'name': 'Amós', 'abbrev': 'Am', 'testament': 'old', 'book_order': 30, 'total_chapters': 9},
            {'name': 'Obadias', 'abbrev': 'Ob', 'testament': 'old', 'book_order': 31, 'total_chapters': 1},
            {'name': 'Jonas', 'abbrev': 'Jn', 'testament': 'old', 'book_order': 32, 'total_chapters': 4},
            {'name': 'Miquéias', 'abbrev': 'Mq', 'testament': 'old', 'book_order': 33, 'total_chapters': 7},
            {'name': 'Naum', 'abbrev': 'Na', 'testament': 'old', 'book_order': 34, 'total_chapters': 3},
            {'name': 'Habacuque', 'abbrev': 'Hc', 'testament': 'old', 'book_order': 35, 'total_chapters': 3},
            {'name': 'Sofonias', 'abbrev': 'Sf', 'testament': 'old', 'book_order': 36, 'total_chapters': 3},
            {'name': 'Ageu', 'abbrev': 'Ag', 'testament': 'old', 'book_order': 37, 'total_chapters': 2},
            {'name': 'Zacarias', 'abbrev': 'Zc', 'testament': 'old', 'book_order': 38, 'total_chapters': 14},
            {'name': 'Malaquias', 'abbrev': 'Ml', 'testament': 'old', 'book_order': 39, 'total_chapters': 4},

            # Novo Testamento
            {'name': 'Mateus', 'abbrev': 'Mt', 'testament': 'new', 'book_order': 40, 'total_chapters': 28},
            {'name': 'Marcos', 'abbrev': 'Mc', 'testament': 'new', 'book_order': 41, 'total_chapters': 16},
            {'name': 'Lucas', 'abbrev': 'Lc', 'testament': 'new', 'book_order': 42, 'total_chapters': 24},
            {'name': 'João', 'abbrev': 'Jo', 'testament': 'new', 'book_order': 43, 'total_chapters': 21},
            {'name': 'Atos', 'abbrev': 'At', 'testament': 'new', 'book_order': 44, 'total_chapters': 28},
            {'name': 'Romanos', 'abbrev': 'Rm', 'testament': 'new', 'book_order': 45, 'total_chapters': 16},
            {'name': '1 Coríntios', 'abbrev': '1Co', 'testament': 'new', 'book_order': 46, 'total_chapters': 16},
            {'name': '2 Coríntios', 'abbrev': '2Co', 'testament': 'new', 'book_order': 47, 'total_chapters': 13},
            {'name': 'Gálatas', 'abbrev': 'Gl', 'testament': 'new', 'book_order': 48, 'total_chapters': 6},
            {'name': 'Efésios', 'abbrev': 'Ef', 'testament': 'new', 'book_order': 49, 'total_chapters': 6},
            {'name': 'Filipenses', 'abbrev': 'Fp', 'testament': 'new', 'book_order': 50, 'total_chapters': 4},
            {'name': 'Colossenses', 'abbrev': 'Cl', 'testament': 'new', 'book_order': 51, 'total_chapters': 4},
            {'name': '1 Tessalonicenses', 'abbrev': '1Ts', 'testament': 'new', 'book_order': 52, 'total_chapters': 5},
            {'name': '2 Tessalonicenses', 'abbrev': '2Ts', 'testament': 'new', 'book_order': 53, 'total_chapters': 3},
            {'name': '1 Timóteo', 'abbrev': '1Tm', 'testament': 'new', 'book_order': 54, 'total_chapters': 6},
            {'name': '2 Timóteo', 'abbrev': '2Tm', 'testament': 'new', 'book_order': 55, 'total_chapters': 4},
            {'name': 'Tito', 'abbrev': 'Tt', 'testament': 'new', 'book_order': 56, 'total_chapters': 3},
            {'name': 'Filemom', 'abbrev': 'Fm', 'testament': 'new', 'book_order': 57, 'total_chapters': 1},
            {'name': 'Hebreus', 'abbrev': 'Hb', 'testament': 'new', 'book_order': 58, 'total_chapters': 13},
            {'name': 'Tiago', 'abbrev': 'Tg', 'testament': 'new', 'book_order': 59, 'total_chapters': 5},
            {'name': '1 Pedro', 'abbrev': '1Pe', 'testament': 'new', 'book_order': 60, 'total_chapters': 5},
            {'name': '2 Pedro', 'abbrev': '2Pe', 'testament': 'new', 'book_order': 61, 'total_chapters': 3},
            {'name': '1 João', 'abbrev': '1Jo', 'testament': 'new', 'book_order': 62, 'total_chapters': 5},
            {'name': '2 João', 'abbrev': '2Jo', 'testament': 'new', 'book_order': 63, 'total_chapters': 1},
            {'name': '3 João', 'abbrev': '3Jo', 'testament': 'new', 'book_order': 64, 'total_chapters': 1},
            {'name': 'Judas', 'abbrev': 'Jd', 'testament': 'new', 'book_order': 65, 'total_chapters': 1},
            {'name': 'Apocalipse', 'abbrev': 'Ap', 'testament': 'new', 'book_order': 66, 'total_chapters': 22},
        ]

        for book_data in books_data:
            book, created = BibleBook.objects.get_or_create(**book_data)
            if created:
                self.stdout.write(f'Livro criado: {book.name}')

        self.stdout.write(self.style.SUCCESS('Bíblia populada com sucesso!'))
