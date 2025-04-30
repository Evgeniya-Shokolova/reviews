from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from reviews.models import AppUser, Genre, Review, Category, Title, Comment

UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('confirmation_code', 'role', 'bio')}),
)
admin.site.register(AppUser, UserAdmin)
admin.site.register(Genre)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(Title)
admin.site.register(Comment)
