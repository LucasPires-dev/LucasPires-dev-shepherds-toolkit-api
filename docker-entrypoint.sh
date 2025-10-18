#!/bin/bash
set -e

export PYTHONPATH=/app:$PYTHONPATH

echo "=========================================="
echo "🚀 INICIANDO SHEPHERD'S TOOLKIT API"
echo "=========================================="

# Aguardar banco
echo "⏳ Aguardando banco de dados..."
while ! nc -z ${DB_HOST:-localhost} ${DB_PORT:-5432}; do
  echo "   Tentando conectar ao banco..."
  sleep 2
done
echo "✓ Banco de dados disponível!"

# Migrations
echo ""
echo "📦 Aplicando migrations..."
cd /app
python manage.py migrate --noinput
echo "✓ Migrations aplicadas!"

# Population Bíblia
if [ "${POPULATE_BIBLE}" = "true" ]; then
  echo ""
  echo "📖 Populando Bíblia..."
  python manage.py populate_bible \
    --source=${BIBLE_SOURCE:-api} \
    --bible-version=${BIBLE_VERSION:-ACF} \
    --clear
  echo "✓ Bíblia populada!"
fi

# Superuser
if [ "${CREATE_SUPERUSER}" = "true" ]; then
  echo ""
  echo "👤 Criando superusuário..."
  python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✓ Superusuário criado!")
END
fi

echo ""
echo "=========================================="
echo "✅ SETUP CONCLUÍDO"
echo "=========================================="

# Executar comando (ou Gunicorn ou runserver)
cd /app
exec "$@"