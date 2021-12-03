from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

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
    user = PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        exclude = ['created']
        model = Follow

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'author']
            )
        ]
