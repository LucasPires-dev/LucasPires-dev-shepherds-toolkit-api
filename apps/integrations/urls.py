from django.urls import path

from .views import (
    GoogleCalendarCallbackView,
    GoogleCalendarDisconnectView,
    GoogleCalendarEventsView,
    GoogleCalendarStatusView,
    KoinoniaAuthorizeView,
    KoinoniaTokenExchangeView,
)

urlpatterns = [
    path('google-calendar/status/', GoogleCalendarStatusView.as_view(), name='google-calendar-status'),
    path('google-calendar/callback/', GoogleCalendarCallbackView.as_view(), name='google-calendar-callback'),
    path('google-calendar/disconnect/', GoogleCalendarDisconnectView.as_view(), name='google-calendar-disconnect'),
    path('google-calendar/events/', GoogleCalendarEventsView.as_view(), name='google-calendar-events'),
    path('koinonia/authorize/', KoinoniaAuthorizeView.as_view(), name='koinonia-authorize'),
    path('koinonia/token/', KoinoniaTokenExchangeView.as_view(), name='koinonia-token-exchange'),
]
