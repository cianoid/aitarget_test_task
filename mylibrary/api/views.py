from rest_framework import viewsets, permissions

from api.permissions import AdminWriteAccessPermission
from api.serializers import (AuthorSerializer, BookSerializer,
                             FollowSerializer, LanguageSerializer)
from library.models import Author, Book, Follow, Language


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AdminWriteAccessPermission]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AdminWriteAccessPermission]


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [AdminWriteAccessPermission]
