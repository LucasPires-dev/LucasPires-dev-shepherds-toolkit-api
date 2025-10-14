from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegistrationSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna dados do usuário logado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Atualiza perfil do usuário logado"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)




class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from .serializers import UserRegistrationSerializer
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'church_name': user.church_name,
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'detail': 'Logout realizado com sucesso'}, status=status.HTTP_200_OK)

    class RegisterView(APIView):
        """Registro de novo usuário"""
        permission_classes = [AllowAny]

        def post(self, request):
            serializer = UserRegistrationSerializer(data=request.data)

            if serializer.is_valid():
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    'token': token.key,
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
        """Login de usuário - usando email e password"""
        permission_classes = [AllowAny]

        def post(self, request):
            email = request.data.get('email')
            password = request.data.get('password')

            # Validação de campos obrigatórios
            if not email or not password:
                return Response(
                    {'error': 'Email e senha são obrigatórios'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Buscar usuário pelo email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Credenciais inválidas'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Autenticar (Django usa username internamente)
            authenticated_user = authenticate(
                username=user.username,
                password=password
            )

            if authenticated_user is not None:
                # Criar ou obter token
                token, created = Token.objects.get_or_create(user=authenticated_user)

                return Response({
                    'token': token.key,
                    'user': UserSerializer(authenticated_user).data
                }, status=status.HTTP_200_OK)

            return Response(
                {'error': 'Credenciais inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

class LogoutView(APIView):
        """Logout - deleta o token do usuário"""
        permission_classes = [IsAuthenticated]

        def post(self, request):
            try:
                # Deletar token do usuário
                request.user.auth_token.delete()
                return Response(
                    {'message': 'Logout realizado com sucesso'},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': 'Erro ao realizar logout'},
                    status=status.HTTP_400_BAD_REQUEST
                )

class MeView(APIView):
        """Retorna dados do usuário autenticado"""
        permission_classes = [IsAuthenticated]

        def get(self, request):
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)