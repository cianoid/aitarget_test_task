from datetime import datetime

from rest_framework import viewsets, permissions, filters

from api.permissions import AdminWriteAccessPermission
from api.serializers import (AuthorSerializer, BookSerializer,
                             FollowSerializer, LanguageSerializer)
from library.models import Author, Book, Follow, Language


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AdminWriteAccessPermission,
                          permissions.IsAuthenticated]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AdminWriteAccessPermission,
                          permissions.IsAuthenticated]
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', 'author__last_name', 'author__first_name')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Book.objects.all()

        return Book.objects.filter(publication_year__lte=datetime.now().year)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [AdminWriteAccessPermission,
                          permissions.IsAuthenticated]
