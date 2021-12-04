from django.contrib import admin

from .models import Author, Book, Follow, Language

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Language)
admin.site.register(Follow)
