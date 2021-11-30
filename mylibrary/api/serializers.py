from django.contrib.auth import get_user_model
from rest_framework import serializers

from library.models import Author, Book, Follow, Language

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Author


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Book


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Follow


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Language
