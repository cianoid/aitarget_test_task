from datetime import datetime

from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from core.email import send_email_using_bcc

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
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('@name', '@author__last_name', '@author__first_name')
    filterset_fields = ('language', 'author')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Book.objects.all()

        return Book.objects.filter(publication_year__lte=datetime.now().year)

    def perform_create(self, serializer):
        serializer.save()

        data = serializer.data
        publication_year = data['publication_year']
        current_year = datetime.now().year

        if publication_year > current_year:
            return None

        author = Author.objects.get(pk=data['author'])
        book_name = data['name']

        followers = author.followers.all()

        if not followers:
            return None

        send_email_using_bcc(
            subject=f'Доступна книга "{book_name}" ({author})',
            message='Привет!\n\n'
                    'Только что на нашем сервисе появилась новая книга от '
                    f'{author}!\n\n'
                    f'{book_name}, {publication_year}г.\n\n'
                    '---'
                    f'\n© {current_year}, Сервис библиотеки ',
            recipient_list=[follower.user.email for follower in followers])


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [AdminWriteAccessPermission,
                          permissions.IsAuthenticated]
