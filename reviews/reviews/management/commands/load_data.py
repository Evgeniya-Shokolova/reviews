import csv
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.conf import settings

from reviews.models import Category, Comment, Genre, Review, Title

DATA_DIR = os.path.join(settings.BASE_DIR, 'static', 'data')
User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка данных из CSV в БД'

    def handle(self, *args, **kwargs):
        try:
            self.load_data(User, 'users.csv', self.load_users)
            self.load_data(Category, 'category.csv', self.load_categories)
            self.load_data(Genre, 'genre.csv', self.load_genres)
            self.load_data(Title, 'titles.csv', self.load_titles)
            self.load_data(Review, 'review.csv', self.load_reviews)
            self.load_data(Comment, 'comments.csv', self.load_comments)
            self.load_genre_title()
            self.stdout.write(
                self.style.SUCCESS('Данные успешно загружены в базу данных.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))

    def load_data(self, model, filename, load_method):
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    load_method(model, row)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка при обработке записи {row}: {e}'))

    def load_users(self, model, row):
        try:
            model.objects.get_or_create(
                id=row['id'],
                defaults={
                    'username': row['username'],
                    'email': row['email'],
                    'role': row['role'],
                    'bio': row['bio'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name']
                }
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при добавлении пользователя {row["username"]}: {e}'))

    def load_categories(self, model, row):
        try:
            model.objects.get_or_create(
                id=row['id'],
                defaults={
                    'name': row['name'],
                    'slug': row['slug']
                }
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при добавлении категории {row["name"]}: {e}'))

    def load_genres(self, model, row):
        try:
            model.objects.get_or_create(
                id=row['id'],
                defaults={
                    'name': row['name'],
                    'slug': row['slug']
                }
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при добавлении жанра {row["name"]}: {e}'))

    def load_titles(self, model, row):
        try:
            model.objects.get_or_create(
                id=row['id'],
                defaults={
                    'name': row['name'],
                    'year': row['year'],
                    'category_id': row['category']
                }
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при добавлении произведения {row["name"]}: {e}'))

    def load_reviews(self, model, row):
        try:
            model.objects.get_or_create(
                id=row['id'],
                defaults={
                    'title_id': row['title_id'],
                    'text': row['text'],
                    'author_id': row['author'],
                    'score': row['score'],
                    'pub_date': row['pub_date']
                }
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при добавлении отзыва {row["id"]}: {e}'))

    def load_comments(self, model, row):
        try:
            model.objects.get_or_create(
                id=row['id'],
                defaults={
                    'review_id': row['review_id'],
                    'text': row['text'],
                    'author_id': row['author'],
                    'pub_date': row['pub_date']
                }
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при добавлении комментария {row["id"]}: {e}'))

    def load_genre_title(self):
        with open(os.path.join(DATA_DIR, 'genre_title.csv'), newline='',
                  encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])
                    title.genre.add(genre)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка при добавлении жанра {row["genre_id"]}'
                        f' к произведению {row["title_id"]}: {e}'))
