from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import LogoutView, RegisterView

urlpatterns = [
    path('login/', obtain_auth_token, name='api-login'),
    path('logout/', LogoutView.as_view(), name='api-logout'),
    path('register/', RegisterView.as_view(), name='api-register'),
]
