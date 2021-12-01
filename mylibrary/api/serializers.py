from django.contrib.auth import get_user_model
from rest_framework import serializers

from library.models import Author, Book, Follow, Language

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['created']
        model = Author


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['created']
        model = Language


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['created']
        model = Book


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['created']
        model = Follow


