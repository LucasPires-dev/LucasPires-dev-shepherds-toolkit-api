#!/bin/bash
set -e

export PYTHONPATH=/app:$PYTHONPATH

# Docker/Swarm secrets: cada arquivo em /run/secrets/<nome> vira a env var
# <NOME EM MAIÚSCULO>, lida normalmente pelo settings via os.getenv. Secret
# vazio não é exportado — deixamos a var indefinida de propósito, para que
# os.getenv('X', default) caia no default do código em vez de receber "".
if [ -d /run/secrets ]; then
  for secret_file in /run/secrets/*; do
    [ -f "$secret_file" ] || continue
    var_name=$(basename "$secret_file" | tr '[:lower:]' '[:upper:]')
    secret_value="$(cat "$secret_file")"
    if [ -n "$secret_value" ]; then
      export "$var_name"="$secret_value"
    fi
  done
fi

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

# Population Bíblia — só roda se ainda não houver versículos dessa versão
# (evita limpar e repopular do zero toda vez que o container reinicia).
if [ "${POPULATE_BIBLE}" = "true" ]; then
  BIBLE_VERSION_TO_CHECK="${BIBLE_VERSION:-ALM1911}"
  EXISTING_VERSES=$(python manage.py shell -c "
from apps.bible.models import BibleVerse
print('VERSE_COUNT:' + str(BibleVerse.objects.filter(version='${BIBLE_VERSION_TO_CHECK}').count()))
" 2>/dev/null | grep '^VERSE_COUNT:' | tail -1 | cut -d: -f2)

  if [ -z "${EXISTING_VERSES}" ]; then
    echo ""
    echo "⚠️  Não foi possível verificar o estado da Bíblia ($BIBLE_VERSION_TO_CHECK) — pulando população por segurança (não populamos automaticamente sem confirmar o estado atual)."
  elif [ "${EXISTING_VERSES}" -ge "${BIBLE_MIN_VERSES:-30000}" ] 2>/dev/null; then
    echo ""
    echo "📖 Bíblia ($BIBLE_VERSION_TO_CHECK) já populada ($EXISTING_VERSES versículos) — pulando."
  else
    echo ""
    echo "📖 Populando Bíblia ($BIBLE_VERSION_TO_CHECK, $EXISTING_VERSES versículos encontrados)..."
    python manage.py populate_bible \
      --source=${BIBLE_SOURCE:-json} \
      --file=${BIBLE_FILE:-ALM1911.json} \
      --bible-version=${BIBLE_VERSION_TO_CHECK} \
      --match-by=${BIBLE_MATCH_BY:-position} \
      --clear
    echo "✓ Bíblia populada!"
  fi
fi

# Superuser
if [ "${CREATE_SUPERUSER}" = "true" ]; then
  if [ -z "${DJANGO_SUPERUSER_PASSWORD}" ]; then
    echo "⚠️  CREATE_SUPERUSER=true mas DJANGO_SUPERUSER_PASSWORD não foi definida. Pulando criação do superusuário."
  else
    echo ""
    echo "👤 Criando superusuário..."
    DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}" \
    DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" \
    DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD}" \
    python manage.py shell << END
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ['DJANGO_SUPERUSER_USERNAME']
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, os.environ['DJANGO_SUPERUSER_EMAIL'], os.environ['DJANGO_SUPERUSER_PASSWORD'])
    print("✓ Superusuário criado!")
else:
    print("✓ Superusuário já existe, mantido.")
END
  fi
fi

echo ""
echo "=========================================="
echo "✅ SETUP CONCLUÍDO"
echo "=========================================="

# Executar comando (ou Gunicorn ou runserver)
cd /app
exec "$@"