import random

from django.contrib.auth.models import AbstractUser
from django.core.validators import (EmailValidator, MaxValueValidator,
                                    MinValueValidator)
from django.db import models

from reviews.constants import (LENGTH_CONFIRMATION_CODE, MAX_LENGTH_COMMENT,
                               MAX_LENGTH_EMAIL, MAX_LENGTH_NAME,
                               MAX_LENGTH_REVIEW, MAX_LENGTH_USERNAME,
                               MAX_NAME_LENGTH, MAX_RATING, MAX_SELF_NAME,
                               MAX_SLUG_CHAR, MIN_RATING, ROLE_ADMIN,
                               ROLE_MODERATOR, ROLE_USER)
from reviews.validators import validate_username, validate_year


class AppUser(AbstractUser):
    """
    Модель описывает специфического пользователя на основе AbstractUser.
    В качестве дополнительных полей используются поля role, bio.
    """
    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[
            validate_username
        ]
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        validators=[
            EmailValidator(
                message='Введите корректный email адрес.',
                code='invalid_email'
            ),
        ]
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_NAME, blank=True, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_NAME, blank=True,
        verbose_name='Фамилия'
    )
    confirmation_code = models.CharField(
        max_length=LENGTH_CONFIRMATION_CODE, blank=True,
        verbose_name='Код подтверждения'
    )
    bio = models.TextField(blank=True, verbose_name='Биография')
    role = models.CharField(
        max_length=max(
            [len(role) for role in (ROLE_USER, ROLE_ADMIN, ROLE_MODERATOR)]),
        choices=(
            (ROLE_USER, 'User'),
            (ROLE_ADMIN, 'Moderator'),
            (ROLE_MODERATOR, 'Admin'),
        ),
        default='user',
        verbose_name='Роль'
    )

    def generate_confirmation_code(self):
        self.confirmation_code = str(random.randint(10000, 99999))

    def save(self, *args, **kwargs):
        """
        Переопределение метода save для автоматической
        генерации кода подтверждения.
        """
        if not self.confirmation_code:
            self.generate_confirmation_code()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_moderator(self):
        return self.role == ROLE_MODERATOR

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN or self.is_superuser or self.is_staff

    def __str__(self):
        return self.username


class BaseModel(models.Model):
    """
    Базовая модель.
    Абстрактная модель, которая содержит общие поля для других моделей,
    такие как название и уникальный идентификатор (slug).
    Все модели, унаследованные от этой, будут иметь упорядочение по названию.
    """
    name = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name="Название"
    )
    slug = models.SlugField(
        unique=True, max_length=MAX_SLUG_CHAR, verbose_name="Идентификатор"
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_SELF_NAME]


class Genre(BaseModel):
    """
    Модель жанра.
    Описывает жанры, к которым могут относиться произведения.
    Каждый жанр имеет уникальный идентификатор (slug) и название.
    """
    class Meta(BaseModel.Meta):
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Category(BaseModel):
    """
    Модель категории.
    Определяет категории произведений, к которым они могут быть отнесены.
    Категории могут использоваться для фильтрации произведений.
    """
    class Meta(BaseModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """
    Модель произведения.
    Описывает произведение, которое может принадлежать к определенной категории
    и иметь несколько жанров.
    Произведения могут иметь отзывы,
    на основе которых рассчитывается средний рейтинг.
    Название ограничено максимальной длиной,
    год проверяется на валидность с помощью функции `validate_year`.
    """
    name = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name="Название"
    )
    year = models.PositiveSmallIntegerField(
        validators=[validate_year], verbose_name="Год"
    )
    description = models.TextField(
        blank=True, verbose_name="Описание"
    )
    genre = models.ManyToManyField(Genre, verbose_name="Жанр")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, verbose_name="Категория"
    )
    
    def generate_confirmation_code(self):
        return str(random.randint(10000, 99999))
    
    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('year', 'name')
        default_related_name = 'titles'

    def __str__(self):
        return self.name[:MAX_SELF_NAME]


class Review(models.Model):
    """
    Модель отзыва.
    Описывает отзыв на произведение,
     который может быть оставлен авторизованным пользователем.
    Отзыв содержит текст, оценку
    (с проверкой на минимальное и максимальное значения),
    дату публикации и связь с произведением.
    Пользователь может оставить только один отзыв на произведение.
    """
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField('текст отзыва')
    author = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    score = models.IntegerField(
        validators=[
            MinValueValidator(MIN_RATING),
            MaxValueValidator(MAX_RATING)
        ]
    )
    pub_date = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text[:MAX_LENGTH_REVIEW]


class Comment(models.Model):
    """
    Модель комментария.
    Описывает комментарий к отзыву, который может быть оставлен пользователем.
    Комментарий содержит текст, дату публикации, связь с отзывом и автором.
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField('текст комментария')
    author = models.ForeignKey(AppUser, on_delete=models.CASCADE,
                               related_name='comments')
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:MAX_LENGTH_COMMENT]