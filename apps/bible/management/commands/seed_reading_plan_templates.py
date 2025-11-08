# Execute estes comandos no terminal:
# python manage.py makemigrations
# python manage.py migrate

# Depois, crie um arquivo de seed data:
# apps/bible/management/commands/seed_reading_plan_templates.py

from django.core.management.base import BaseCommand
from apps.bible.models import ReadingPlanTemplate


class Command(BaseCommand):
    help = 'Popula templates de planos de leitura'

    def handle(self, *args, **options):
        templates = [
            {
                'id': 'bible_year',
                'name': 'Bíblia em 1 Ano',
                'description': 'Leia toda a Bíblia em 365 dias com um plano equilibrado entre AT e NT',
                'plan_type': 'bible_year',
                'duration_days': 365,
                'icon': '📖',
                'color': 'from-blue-500 to-blue-600',
                'readings_count': 365,
                'readings_data': self.get_bible_year_readings()
            },
            {
                'id': 'nt_90days',
                'name': 'Novo Testamento em 90 Dias',
                'description': 'Complete todo o Novo Testamento em apenas 3 meses',
                'plan_type': 'nt_90days',
                'duration_days': 90,
                'icon': '✝️',
                'color': 'from-green-500 to-green-600',
                'readings_count': 90,
                'readings_data': self.get_nt_90days_readings()
            },
            {
                'id': 'psalms_month',
                'name': 'Salmos em 1 Mês',
                'description': 'Medite em 5 salmos por dia durante 30 dias',
                'plan_type': 'psalms_month',
                'duration_days': 30,
                'icon': '🎵',
                'color': 'from-purple-500 to-purple-600',
                'readings_count': 150,
                'readings_data': self.get_psalms_month_readings()
            },
            {
                'id': 'gospels_40days',
                'name': 'Evangelhos em 40 Dias',
                'description': 'Conheça a vida de Jesus através dos 4 evangelhos',
                'plan_type': 'custom',
                'duration_days': 40,
                'icon': '🕊️',
                'color': 'from-pink-500 to-pink-600',
                'readings_count': 89,
                'readings_data': self.get_gospels_40days_readings()
            },
            {
                'id': 'proverbs_month',
                'name': 'Provérbios em 1 Mês',
                'description': 'Um capítulo de sabedoria por dia durante um mês',
                'plan_type': 'custom',
                'duration_days': 31,
                'icon': '💡',
                'color': 'from-yellow-500 to-yellow-600',
                'readings_count': 31,
                'readings_data': self.get_proverbs_month_readings()
            }
        ]

        for template_data in templates:
            template, created = ReadingPlanTemplate.objects.update_or_create(
                id=template_data['id'],
                defaults=template_data
            )
            action = 'Criado' if created else 'Atualizado'
            self.stdout.write(
                self.style.SUCCESS(f'{action}: {template.name}')
            )

    def get_bible_year_readings(self):
        """Retorna leituras para Bíblia em 1 ano"""
        # Esta é uma versão simplificada.
        # Você precisaria de um plano completo de 365 dias
        readings = []
        for day in range(1, 366):
            readings.append([
                {
                    'book': 'Gênesis',
                    'book_id': 1,
                    'chapters': [day],
                    'reference': f'Gênesis {day}'
                }
            ])
        return readings

    def get_nt_90days_readings(self):
        """Retorna leituras para NT em 90 dias"""
        readings = []
        nt_books = [
            ('Mateus', 40, 28),
            ('Marcos', 41, 16),
            ('Lucas', 42, 24),
            ('João', 43, 21),
            # ... adicione todos os livros do NT
        ]

        day = 1
        for book_name, book_id, chapters in nt_books:
            for chapter in range(1, chapters + 1):
                if day <= 90:
                    readings.append([{
                        'book': book_name,
                        'book_id': book_id,
                        'chapters': [chapter],
                        'reference': f'{book_name} {chapter}'
                    }])
                    day += 1

        return readings

    def get_psalms_month_readings(self):
        """Retorna leituras para Salmos em 1 mês"""
        readings = []
        psalms_per_day = 5

        for day in range(1, 31):
            start_psalm = (day - 1) * psalms_per_day + 1
            end_psalm = min(start_psalm + psalms_per_day - 1, 150)
            chapters = list(range(start_psalm, end_psalm + 1))

            readings.append([{
                'book': 'Salmos',
                'book_id': 19,
                'chapters': chapters,
                'reference': f'Salmos {start_psalm}-{end_psalm}'
            }])

        return readings

    def get_gospels_40days_readings(self):
        """Retorna leituras para Evangelhos em 40 dias"""
        readings = []
        gospels = [
            ('Mateus', 40, 28),
            ('Marcos', 41, 16),
            ('Lucas', 42, 24),
            ('João', 43, 21),
        ]

        day = 1
        for book_name, book_id, chapters in gospels:
            for chapter in range(1, chapters + 1):
                if day <= 40:
                    readings.append([{
                        'book': book_name,
                        'book_id': book_id,
                        'chapters': [chapter],
                        'reference': f'{book_name} {chapter}'
                    }])
                    day += 1

        return readings

    def get_proverbs_month_readings(self):
        """Retorna leituras para Provérbios em 1 mês"""
        readings = []
        for day in range(1, 32):
            readings.append([{
                'book': 'Provérbios',
                'book_id': 20,
                'chapters': [day],
                'reference': f'Provérbios {day}'
            }])

        return readings