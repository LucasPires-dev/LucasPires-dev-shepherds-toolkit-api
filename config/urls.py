from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importações existentes
from apps.users.views import UserViewSet
from apps.bible.views import (
    BibleBookViewSet, 
    BibleVerseViewSet, 
    VerseHighlightViewSet, 
    VerseNoteViewSet
)

# Reading Plan imports
from apps.bible.reading_plan_views import (
    ReadingPlanTemplateViewSet,
    UserReadingPlanViewSet,
    ReadingDayViewSet
)

from apps.writings.views import WritingViewSet, WritingTagViewSet
from apps.goals.views import GoalViewSet, GoalTaskViewSet, GoalCommentViewSet
from apps.events.views import EventViewSet
from apps.members.views import MemberViewSet, PastoralVisitViewSet
from apps.prayers.views import PrayerRequestViewSet
from apps.finances.views import FinanceViewSet
from apps.investments.views import InvestmentViewSet
from apps.library.views import LibraryResourceViewSet, LibraryHighlightViewSet
from apps.notifications.views import NotificationViewSet

# Criar router principal
router = DefaultRouter()

# User routes
router.register(r'users', UserViewSet, basename='user')

# Bible routes
router.register(r'bible/books', BibleBookViewSet, basename='bible-book')
router.register(r'bible/verses', BibleVerseViewSet, basename='bible-verse')
router.register(r'bible/highlights', VerseHighlightViewSet, basename='verse-highlight')
router.register(r'bible/notes', VerseNoteViewSet, basename='verse-note')

# ✅ CORREÇÃO: Reading Plan routes (ordem correta - mais específico primeiro)
# Templates primeiro (read-only)
router.register(r'reading-plans/templates', ReadingPlanTemplateViewSet, basename='reading-plan-template')
# Depois os user plans
router.register(r'reading-plans', UserReadingPlanViewSet, basename='reading-plan')

# ⚠️ IMPORTANTE: Não registre ReadingDayViewSet no router principal
# Ele será acessado através de actions na UserReadingPlanViewSet ou via endpoints específicos

# Writing routes
router.register(r'writings', WritingViewSet, basename='writing')
router.register(r'writing-tags', WritingTagViewSet, basename='writing-tag')

# Goal routes
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'goal-tasks', GoalTaskViewSet, basename='goal-task')
router.register(r'goal-comments', GoalCommentViewSet, basename='goal-comment')

# Event routes
router.register(r'events', EventViewSet, basename='event')

# Member routes
router.register(r'members', MemberViewSet, basename='member')
router.register(r'pastoral-visits', PastoralVisitViewSet, basename='pastoral-visit')

# Prayer routes
router.register(r'prayer-requests', PrayerRequestViewSet, basename='prayer-request')

# Finance routes
router.register(r'finances', FinanceViewSet, basename='finance')
router.register(r'investments', InvestmentViewSet, basename='investment')

# Library routes
router.register(r'library/resources', LibraryResourceViewSet, basename='library-resource')
router.register(r'library/highlights', LibraryHighlightViewSet, basename='library-highlight')

# Notification routes
router.register(r'notifications', NotificationViewSet, basename='notification')

# ✅ Router separado para Reading Days (se necessário acesso direto)
reading_days_router = DefaultRouter()
reading_days_router.register(r'', ReadingDayViewSet, basename='reading-day')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/auth/token/', include('apps.users.auth_urls')),
    # ✅ Endpoint separado para reading days se necessário
    path('api/v1/reading-days/', include(reading_days_router.urls)),
    path('api/v1/ai/', include('apps.ai.urls')),
    path('api/v1/integrations/', include('apps.integrations.urls')),
]