# =====================================================
# apps/bible/management/commands/populate_bible.py
# =====================================================

from django.core.management.base import BaseCommand, CommandError
from apps.bible.models import BibleBook, BibleVerse
import json
import requests
from pathlib import Path


class Command(BaseCommand):
    help = 'Popula o banco de dados com livros e versículos da Bíblia'

    def add_arguments(self, parser):
        """Adiciona argumentos opcionais ao comando"""
        parser.add_argument(
            '--source',
            type=str,
            default='json',
            choices=['json', 'api'],
            help='Fonte dos dados: json (arquivo local) ou api (API externa)'
        )
        
        parser.add_argument(
            '--bible-version',
            type=str,
            default='ACF',
            dest='bible_version',
            help='Versão da Bíblia (ACF, NVI, ARA, etc.)'
        )
        
        parser.add_argument(
            '--file',
            type=str,
            default='bible_data.json',
            help='Caminho do arquivo JSON com dados da Bíblia'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa dados existentes antes de popular'
        )

    def handle(self, *args, **options):
        """Método principal que executa o comando"""
        
        source = options['source']
        version = options['bible_version']  # Mudou de 'version' para 'bible_version'
        clear_data = options['clear']
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('🙏 INICIANDO POPULAÇÃO DA BÍBLIA'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # Limpar dados se solicitado
        if clear_data:
            self.clear_existing_data()
        
        # Popular livros
        self.stdout.write('\n📚 Populando livros da Bíblia...')
        self.populate_books()
        
        # Popular versículos
        self.stdout.write('\n📖 Populando versículos...')
        if source == 'json':
            file_path = options['file']
            self.populate_verses_from_json(file_path, version)
        else:
            self.populate_verses_from_api(version)
        
        # Estatísticas finais
        self.show_statistics()
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!'))
        self.stdout.write(self.style.SUCCESS('=' * 70 + '\n'))

    def clear_existing_data(self):
        """Limpa dados existentes do banco"""
        self.stdout.write(self.style.WARNING('\n⚠️  Limpando dados existentes...'))
        
        verse_count = BibleVerse.objects.count()
        book_count = BibleBook.objects.count()
        
        BibleVerse.objects.all().delete()
        BibleBook.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'   ✓ {verse_count} versículos removidos\n'
                f'   ✓ {book_count} livros removidos'
            )
        )

    def populate_books(self):
        """Popula livros da Bíblia"""
        
        # Lista completa dos 66 livros da Bíblia
        books_data = [
            # ANTIGO TESTAMENTO
            # Pentateuco
            {'name': 'Gênesis', 'abbrev': 'Gn', 'testament': 'old', 'book_order': 1, 'total_chapters': 50},
            {'name': 'Êxodo', 'abbrev': 'Ex', 'testament': 'old', 'book_order': 2, 'total_chapters': 40},
            {'name': 'Levítico', 'abbrev': 'Lv', 'testament': 'old', 'book_order': 3, 'total_chapters': 27},
            {'name': 'Números', 'abbrev': 'Nm', 'testament': 'old', 'book_order': 4, 'total_chapters': 36},
            {'name': 'Deuteronômio', 'abbrev': 'Dt', 'testament': 'old', 'book_order': 5, 'total_chapters': 34},
            
            # Livros Históricos
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
            
            # Livros Poéticos
            {'name': 'Jó', 'abbrev': 'Jó', 'testament': 'old', 'book_order': 18, 'total_chapters': 42},
            {'name': 'Salmos', 'abbrev': 'Sl', 'testament': 'old', 'book_order': 19, 'total_chapters': 150},
            {'name': 'Provérbios', 'abbrev': 'Pv', 'testament': 'old', 'book_order': 20, 'total_chapters': 31},
            {'name': 'Eclesiastes', 'abbrev': 'Ec', 'testament': 'old', 'book_order': 21, 'total_chapters': 12},
            {'name': 'Cânticos', 'abbrev': 'Ct', 'testament': 'old', 'book_order': 22, 'total_chapters': 8},
            
            # Profetas Maiores
            {'name': 'Isaías', 'abbrev': 'Is', 'testament': 'old', 'book_order': 23, 'total_chapters': 66},
            {'name': 'Jeremias', 'abbrev': 'Jr', 'testament': 'old', 'book_order': 24, 'total_chapters': 52},
            {'name': 'Lamentações', 'abbrev': 'Lm', 'testament': 'old', 'book_order': 25, 'total_chapters': 5},
            {'name': 'Ezequiel', 'abbrev': 'Ez', 'testament': 'old', 'book_order': 26, 'total_chapters': 48},
            {'name': 'Daniel', 'abbrev': 'Dn', 'testament': 'old', 'book_order': 27, 'total_chapters': 12},
            
            # Profetas Menores
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
            
            # NOVO TESTAMENTO
            # Evangelhos
            {'name': 'Mateus', 'abbrev': 'Mt', 'testament': 'new', 'book_order': 40, 'total_chapters': 28},
            {'name': 'Marcos', 'abbrev': 'Mc', 'testament': 'new', 'book_order': 41, 'total_chapters': 16},
            {'name': 'Lucas', 'abbrev': 'Lc', 'testament': 'new', 'book_order': 42, 'total_chapters': 24},
            {'name': 'João', 'abbrev': 'Jo', 'testament': 'new', 'book_order': 43, 'total_chapters': 21},
            
            # História
            {'name': 'Atos', 'abbrev': 'At', 'testament': 'new', 'book_order': 44, 'total_chapters': 28},
            
            # Cartas Paulinas
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
            
            # Cartas Gerais
            {'name': 'Hebreus', 'abbrev': 'Hb', 'testament': 'new', 'book_order': 58, 'total_chapters': 13},
            {'name': 'Tiago', 'abbrev': 'Tg', 'testament': 'new', 'book_order': 59, 'total_chapters': 5},
            {'name': '1 Pedro', 'abbrev': '1Pe', 'testament': 'new', 'book_order': 60, 'total_chapters': 5},
            {'name': '2 Pedro', 'abbrev': '2Pe', 'testament': 'new', 'book_order': 61, 'total_chapters': 3},
            {'name': '1 João', 'abbrev': '1Jo', 'testament': 'new', 'book_order': 62, 'total_chapters': 5},
            {'name': '2 João', 'abbrev': '2Jo', 'testament': 'new', 'book_order': 63, 'total_chapters': 1},
            {'name': '3 João', 'abbrev': '3Jo', 'testament': 'new', 'book_order': 64, 'total_chapters': 1},
            {'name': 'Judas', 'abbrev': 'Jd', 'testament': 'new', 'book_order': 65, 'total_chapters': 1},
            
            # Profecia
            {'name': 'Apocalipse', 'abbrev': 'Ap', 'testament': 'new', 'book_order': 66, 'total_chapters': 22},
        ]
        
        created_count = 0
        for book_data in books_data:
            book, created = BibleBook.objects.get_or_create(**book_data)
            if created:
                created_count += 1
                self.stdout.write(f'   ✓ {book.name} ({book.abbrev})')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n   📚 {created_count} livros criados com sucesso!')
        )

    def populate_verses_from_json(self, file_path, version):
        """Popula versículos a partir de arquivo JSON"""
        
        try:
            # Tentar diferentes caminhos para o arquivo
            possible_paths = [
                Path(file_path),
                Path('data') / file_path,
                Path('apps/bible/data') / file_path,
            ]
            
            json_file = None
            for path in possible_paths:
                if path.exists():
                    json_file = path
                    break
            
            if not json_file:
                raise FileNotFoundError(
                    f'Arquivo não encontrado. Procurado em: {[str(p) for p in possible_paths]}'
                )
            
            self.stdout.write(f'   📄 Lendo arquivo: {json_file}')
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            verses_created = 0
            total_verses = sum(len(chapters) for book in data for chapters in book.get('chapters', []))
            
            self.stdout.write(f'   📊 Total de versículos a processar: {total_verses}')
            
            for book_data in data:
                book_name = book_data.get('name')
                
                try:
                    book = BibleBook.objects.get(name=book_name)
                except BibleBook.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'   ⚠️  Livro não encontrado: {book_name}')
                    )
                    continue
                
                for chapter_num, chapter_verses in enumerate(book_data.get('chapters', []), start=1):
                    for verse_num, verse_text in enumerate(chapter_verses, start=1):
                        BibleVerse.objects.create(
                            book=book,
                            chapter=chapter_num,
                            verse=verse_num,
                            text=verse_text,
                            version=version
                        )
                        verses_created += 1
                        
                        # Progress indicator
                        if verses_created % 1000 == 0:
                            self.stdout.write(f'   📖 {verses_created}/{total_verses} versículos processados...')
                
                self.stdout.write(f'   ✓ {book.name} completo')
            
            self.stdout.write(
                self.style.SUCCESS(f'\n   📖 {verses_created} versículos criados com sucesso!')
            )
            
        except FileNotFoundError as e:
            raise CommandError(f'Erro ao ler arquivo JSON: {e}')
        except json.JSONDecodeError as e:
            raise CommandError(f'Erro ao parsear JSON: {e}')
        except Exception as e:
            raise CommandError(f'Erro inesperado: {e}')

    def populate_verses_from_api(self, version):
        """Popula versículos a partir de API externa"""
        
        self.stdout.write('   🌐 Buscando dados da API...')
        
        # Exemplo usando API pública (você pode trocar pela API que preferir)
        api_urls = {
            'ACF': 'https://raw.githubusercontent.com/thiagobodruk/bible/master/json/pt_acf.json',
            'NVI': 'https://raw.githubusercontent.com/thiagobodruk/bible/master/json/pt_nvi.json',
        }
        
        api_url = api_urls.get(version)
        if not api_url:
            raise CommandError(f'API não configurada para versão: {version}')
        
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            verses_created = 0
            
            for book_data in data:
                book_abbrev = book_data.get('abbrev', {}).get('pt')
                
                try:
                    book = BibleBook.objects.get(abbrev=book_abbrev)
                except BibleBook.DoesNotExist:
                    continue
                
                for chapter in book_data.get('chapters', []):
                    chapter_num = chapter[0]
                    for verse_num, verse_text in chapter[1:]:
                        BibleVerse.objects.create(
                            book=book,
                            chapter=chapter_num,
                            verse=verse_num,
                            text=verse_text,
                            version=version
                        )
                        verses_created += 1
                
                self.stdout.write(f'   ✓ {book.name} completo')
            
            self.stdout.write(
                self.style.SUCCESS(f'\n   📖 {verses_created} versículos criados com sucesso!')
            )
            
        except requests.RequestException as e:
            raise CommandError(f'Erro ao acessar API: {e}')
        except Exception as e:
            raise CommandError(f'Erro inesperado: {e}')

    def show_statistics(self):
        """Mostra estatísticas finais"""
        
        total_books = BibleBook.objects.count()
        total_verses = BibleVerse.objects.count()
        old_testament = BibleBook.objects.filter(testament='old').count()
        new_testament = BibleBook.objects.filter(testament='new').count()
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('📊 ESTATÍSTICAS FINAIS'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'   📚 Total de livros: {total_books}')
        self.stdout.write(f'   📖 Antigo Testamento: {old_testament} livros')
        self.stdout.write(f'   📖 Novo Testamento: {new_testament} livros')
        self.stdout.write(f'   📝 Total de versículos: {total_verses}')
