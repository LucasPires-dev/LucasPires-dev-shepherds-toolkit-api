from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from apps.users.models import User
from .models import GoogleCalendarConnection


class GoogleCalendarStatusTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='smoketest', email='smoke@test.com', password='pass12345')
        self.client.force_authenticate(user=self.user)

    def test_status_disconnected_by_default(self):
        response = self.client.get('/api/integrations/google-calendar/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'connected': False})

    def test_status_connected(self):
        connection = GoogleCalendarConnection(
            user=self.user,
            google_email='pastor@example.com',
            access_token='fake-access',
            access_token_expires_at=timezone.now(),
        )
        connection.refresh_token = 'fake-refresh'
        connection.save()

        response = self.client.get('/api/integrations/google-calendar/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['connected'])
        self.assertEqual(response.data['google_email'], 'pastor@example.com')

        # Refresh token round-trips through Fernet encryption correctly.
        connection.refresh_from_db()
        self.assertEqual(connection.refresh_token, 'fake-refresh')

    def test_disconnect_removes_connection(self):
        connection = GoogleCalendarConnection(
            user=self.user,
            google_email='pastor@example.com',
            access_token='fake-access',
            access_token_expires_at=timezone.now(),
        )
        connection.refresh_token = 'fake-refresh'
        connection.save()

        response = self.client.post('/api/integrations/google-calendar/disconnect/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(GoogleCalendarConnection.objects.filter(user=self.user).exists())
