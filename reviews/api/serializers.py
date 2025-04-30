from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.validators import ValidationError

from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Comment, Genre, Review, Title, AppUser
from reviews.constants import MAX_LENGTH_EMAIL, MAX_LENGTH_USERNAME
from reviews.validators import validate_username

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователей, обеспечивающий валидацию
    и сериализацию полей, необходимых для регистрации."""

    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        validators=[validate_username]
    )
    email = serializers.EmailField(
        max_length=MAX_LENGTH_EMAIL
    )

    def send_confirmation_code(self, user):
        send_mail(
            'Код подтверждения для регистрации на YaMDB',
            f'Ваш код подтверждения: {user.confirmation_code}',
            'admin@yamdb.com',
            [user.email],
            fail_silently=False,
        )

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        if AppUser.objects.filter(email=email).exists():
            if not AppUser.objects.filter(
                username=username, email=email).exists():
                raise serializers.ValidationError({
                    'email': 'Email уже используется с другим username.'
                })

        if AppUser.objects.filter(username=username).exists():
            user = AppUser.objects.get(username=username)
            if user.email != email:
                raise serializers.ValidationError({
                    'username': 'Username уже используется с другим email.'
                })
            return user

        user = AppUser.objects.create(**validated_data)
        self.send_confirmation_code(user)
        return user


class AppUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели AppUser, обеспечивающий валидацию
    и сериализацию полей пользователя.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role',)


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для получения токена доступа,
    обеспечивающий валидацию
    и сериализацию полей username, confirmation_code.
    """
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        """Валидация данных для получения токена."""
        user = get_object_or_404(User, username=data['username'])
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError('Неверный код подтверждения.')

        return data

    def get_token(self, user):
        """Получает JWT токен для указанного пользователя."""
        return str(AccessToken.for_user(user).access_token)


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для категории, включает поля 'name' и 'slug'.
    """
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для жанра, включает поля 'name' и 'slug'.
    """
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения информации о произведениях,
    включает связанные жанры, категорию и рейтинг.
    """
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(default=None)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')
        read_only_fields = ('rating',)


class TitleCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления произведений,
    использует поля slug для жанров и категории.
    """
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True, allow_null=False, allow_empty=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def to_representation(self, title):
        serializer = TitleReadSerializer(title)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отзывов, включает проверку на наличие
    одного отзыва от пользователя на произведение.
    """
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        """Валидация на количество отзывов не более одного."""
        request = self.context['request']
        if request.method == 'POST':
            author = request.user
            title_id = self.context['view'].kwargs.get('title_id')

            if Review.objects.filter(title_id=title_id,
                                     author=author).exists():
                raise ValidationError('Можно оставить только один отзыв!')
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для комментариев к отзывам,
    включает автора и дату публикации.
    """
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    pub_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ",
                                         read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
