from django.contrib.auth import get_user_model
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.base_viewset import BaseReadOnlyViewSet
from api.permissions import IsAdmin, IsAdminOrReadOnly, RoleBasedPermission
from api.serializers import (AppUserSerializer, CategorySerializer,
                             CommentSerializer, GenreSerializer,
                             ReviewSerializer, SignUpSerializer,
                             TitleCreateSerializer, TitleReadSerializer,
                             TokenObtainSerializer)
from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter

User = get_user_model()


class SignupViewSet(viewsets.ModelViewSet):
    """
    Представление  для регистрации новых пользователей.
    """
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]
    http_method_names = ('post',)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.validated_data, status=status.HTTP_200_OK)


class TokenObtainView(APIView):
    """
    Представление для получения токена доступа по username и коду
    подтверждения.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data['username'])
        token = serializer.get_token(user)
        user.is_active = True
        user.save()
        return Response({"token": token}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    Представление для управления пользователями.
    Доступ разрешен только администратору.
    """
    permission_classes = (IsAuthenticated, IsAdmin,)
    queryset = User.objects.all()
    serializer_class = AppUserSerializer
    lookup_field = 'username'
    http_method_names = ('get', 'patch', 'delete', 'post',)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=(IsAuthenticated, RoleBasedPermission,))
    def me(self, request):
        """
        Эндпоинт для получения и обновления данных текущего пользователя.
        """
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data)


class TitleViewSet(viewsets.ModelViewSet):
    """
    Представление для произведений (Title).
    Поддерживает операции CRUD для произведений.
    Произведения автоматически аннотируются средним рейтингом
    на основе отзывов.
    Администраторам доступно создание, обновление и удаление произведений,
    пользователи могут только просматривать.
    """
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('year', 'name')
    pagination_class = pagination.LimitOffsetPagination
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleReadSerializer

        return TitleCreateSerializer


class CategoryViewSet(BaseReadOnlyViewSet):
    """
    Представление для категорий.
    Обеспечивает доступ только для чтения (список категорий и детализация).
    Фильтрация категорий по имени.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseReadOnlyViewSet):
    """
    Представление для жанров.
    Обеспечивает доступ только для чтения (список жанров и детализация).
    Фильтрация жанров по имени.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Представление для отзывов на произведения.
    Поддерживает операции CRUD для отзывов.
    Отзывы фильтруются по произведению, с возможностью создания отзывов
    авторизованными пользователями.
    """
    serializer_class = ReviewSerializer
    permission_classes = (RoleBasedPermission,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        """Получение объекта произведения по ID."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Фильтруем отзывы для конкретного произведения."""
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        """Сохраняет отзыв с текущим пользователем как автором."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Представление для комментариев к отзывам.
    Поддерживает операции CRUD для комментариев к отзывам.
    Комментарии фильтруются по конкретному отзыву, с возможностью создания
    комментариев авторизованными пользователями.
    """
    permission_classes = (RoleBasedPermission,)
    serializer_class = CommentSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        """Получение объекта отзыва по ID."""
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id, title__id=title_id)

    def get_queryset(self):
        """Фильтруем комментарии для конкретного отзыва."""
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        """Сохраняет комментарий с текущим пользователем как автором."""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
