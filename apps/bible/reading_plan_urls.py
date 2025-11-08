from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .reading_plan_views import (
    ReadingPlanTemplateViewSet,
    UserReadingPlanViewSet,
    ReadingDayViewSet
)

router = DefaultRouter()
router.register(r'templates', ReadingPlanTemplateViewSet, basename='reading-plan-templates')
router.register(r'', UserReadingPlanViewSet, basename='reading-plans')
router.register(r'readings', ReadingDayViewSet, basename='reading-days')

urlpatterns = [
    path('', include(router.urls)),
]