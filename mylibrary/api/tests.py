from datetime import datetime

from django.contrib.auth import get_user_model
from django.core import mail
from django.shortcuts import get_object_or_404
from django.urls import include, path
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase, URLPatternsTestCase

from library.models import Author, Book, Follow, Language

User = get_user_model()


class APITests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('api/', include('api.urls')),
    ]

    author_ru: Author
    author_en: Author
    author_fr: Author

    lang_ru: Language
    lang_en: Language
    lang_fr: Language

    book_ru: Book
    book_en: Book
    book_fr: Book
    book_ru_from_future: Book

    languages_count: int
    authors_count: int
    books_count: int
    books_count_for_user: int
    books_count_for_staff: int

    staff: User
    staff_login = 'admin'
    staff_password = 'admin-pass'
    staff_email = 'admin@example.com'
    staff_client: APIClient

    user: User
    user_login = 'user'
    user_password = 'user-pass'
    user_email = 'user@example.com'
    user_client: APIClient

    test_author_data = {
        'first_name': 'Федор',
        'middle_name': 'Михайлович',
        'last_name': 'Достоевский'
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.lang_ru = Language.objects.create(name='Русский')
        cls.lang_en = Language.objects.create(name='Английский')
        cls.lang_fr = Language.objects.create(name='Французский')
        cls.languages_count = Language.objects.all().count()

        cls.author_ru = Author.objects.create(
            first_name='Лев', middle_name='Николаевич', last_name='Толстой')
        cls.author_en = Author.objects.create(
            first_name='Уильям', last_name='Шекспир')
        cls.author_fr = Author.objects.create(
            first_name='Жюль', last_name='Верн')
        cls.authors_count = Author.objects.all().count()

        cls.book_ru = Book.objects.create(
            name='Война и Мир', publication_year=1867, language=cls.lang_ru,
            author=cls.author_ru)
        cls.book_en = Book.objects.create(
            name='Ромео и Джульетта', publication_year=1597,
            language=cls.lang_en, author=cls.author_en)
        cls.book_fr = Book.objects.create(
            name='20000 лье под водой', publication_year=1869,
            language=cls.lang_fr, author=cls.author_fr)
        cls.book_ru_from_future = Book.objects.create(
            name='Про космос', publication_year=2025, language=cls.lang_ru,
            author=cls.author_ru)
        cls.books_count_for_user = Book.objects.filter(
            publication_year__lte=datetime.now().year).count()
        cls.books_count_for_staff = Book.objects.all().count()
        cls.books_count = Book.objects.all().count()

        cls.user = User.objects.create_user(cls.user_login, cls.user_password)
        cls.staff = User.objects.create_user(
            cls.staff_login, cls.staff_email, cls.staff_password, is_staff=1)

    @classmethod
    def tearDownClass(cls):
        Book.objects.all().delete()
        Author.objects.all().delete()
        Language.objects.all().delete()
        Follow.objects.all().delete()
        User.objects.all().delete()

    def setUp(self):
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)

        self.staff_client = APIClient()
        self.staff_client.force_authenticate(user=self.staff)

    def anon_access(self, url_list, url_detail):
        endpoints = {
            'get': [url_list, url_detail],
            'post': [url_list],
            'patch': [url_detail],
            'put': [url_detail],
            'delete': [url_detail]
        }

        for method, addresses in endpoints.items():
            for address in addresses:
                with self.subTest(address=address):
                    response = getattr(self.client, method)(address)

                    self.assertEqual(
                        status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_anon_cant_access_language(self):
        url_list = reverse('api:languages-list')
        url_detail = reverse('api:languages-detail', args=[self.lang_ru.pk])

        return self.anon_access(url_list, url_detail)

    def test_staff_can_read_language(self):
        url = reverse('api:languages-detail', args=[self.lang_ru.pk])
        response = self.staff_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.lang_ru.name)

    def test_staff_can_list_language(self):
        url = reverse('api:languages-list')
        response = self.staff_client.get(url)

        item = response.data[1]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Language.objects.get(pk=item['id']).name, item['name'])

    def test_staff_can_create_language(self):
        url = reverse('api:languages-list')
        data = {'name': 'Иврит'}

        response = self.staff_client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Language.objects.count(), self.languages_count + 1)

        Language.objects.filter(name=data['name']).delete()

    def test_staff_can_partial_update_language(self):
        language = Language.objects.create(name='Китайкий')

        url = reverse('api:languages-detail', args=[language.pk])
        data = {'name': 'Китайский'}

        response = self.staff_client.patch(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Language.objects.get(pk=language.pk).name, data['name'])

        language.delete()

    def test_staff_can_update_language(self):
        language = Language.objects.create(name='Китайкий')

        url = reverse('api:languages-detail', args=[language.pk])
        data = {'name': 'Китайский'}

        response = self.staff_client.put(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Language.objects.get(pk=language.pk).name, data['name'])

        language.delete()

    def test_staff_can_delete_language(self):
        language = Language.objects.create(name='Китасйкий')

        url = reverse('api:languages-detail', args=[language.pk])

        response = self.staff_client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Language.objects.count(), self.languages_count)
        self.assertEqual(Language.objects.filter(pk=language.pk).count(), 0)

        language.delete()

    def test_user_can_read_language(self):
        url = reverse('api:languages-detail', args=[self.lang_ru.pk])
        response = self.user_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.lang_ru.name)

    def test_user_can_list_language(self):
        url = reverse('api:languages-list')
        response = self.user_client.get(url)

        item = response.data[1]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Language.objects.get(pk=item['id']).name, item['name'])

    def test_user_cant_create_language(self):
        url = reverse('api:languages-list')
        data = {'name': 'Иврит'}

        response = self.user_client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Language.objects.count(), self.languages_count)

    def test_user_cant_partial_update_language(self):
        language = Language.objects.create(name='Китайкий')

        url = reverse('api:languages-detail', args=[language.pk])
        data = {'name': 'Китайский'}

        response = self.user_client.patch(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Language.objects.get(pk=language.pk).name, data['name'])

        language.delete()

    def test_user_cant_update_language(self):
        language = Language.objects.create(name='Китайкий')

        url = reverse('api:languages-detail', args=[language.pk])
        data = {'name': 'Китайский'}

        response = self.user_client.put(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Language.objects.get(pk=language.pk).name, data['name'])

        language.delete()

    def test_user_cant_delete_language(self):
        language = Language.objects.create(name='Китайский')

        url = reverse('api:languages-detail', args=[language.pk])

        response = self.user_client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Language.objects.count(), self.languages_count + 1)
        self.assertEqual(Language.objects.filter(pk=language.pk).count(), 1)

        language.delete()

    def test_anon_cant_access_book(self):
        url_list = reverse('api:books-list')
        url_detail = reverse('api:books-detail', args=[self.book_ru.pk])

        return self.anon_access(url_list, url_detail)

    def test_staff_can_read_book(self):
        url = reverse('api:books-detail', args=[self.book_ru_from_future.pk])
        response = self.staff_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.book_ru_from_future.name)

    def test_staff_can_search_book(self):
        reversed = reverse('api:books-list')

        url = '{}?search={}'.format(reversed, 'толстой,война')

        response = self.staff_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        url = '{}?search={}'.format(reversed, 'Толстой')
        response = self.staff_client.get(url)

        item = response.data[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            Book.objects.get(pk=item['id']).name, item['name'])

    def test_staff_can_list_book(self):
        url = reverse('api:books-list')
        response = self.staff_client.get(url)

        item = response.data[1]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.books_count_for_staff)
        self.assertEqual(
            Book.objects.get(pk=item['id']).name, item['name'])

    def test_staff_can_create_book(self):
        url = reverse('api:books-list')
        data = {'name': 'Власть тьмы', 'publication_year': 1887,
                'author': self.author_ru.pk, 'language': self.lang_ru.pk}

        response = self.staff_client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), self.books_count + 1)

        Book.objects.get(name=data['name']).delete()

    def test_staff_can_partial_update_book(self):
        book = Book.objects.create(
            name='Влаь тьмы', publication_year=1887, author=self.author_ru,
            language=self.lang_ru)

        url = reverse('api:books-detail', args=[book.pk])
        data = {'name': 'Власть тьмы'}

        response = self.staff_client.patch(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Book.objects.get(pk=book.pk).name, data['name'])

        book.delete()

    def test_staff_can_update_book(self):
        book_data = {'name': 'Влаь тьмы', 'publication_year': 1887}

        book = Book.objects.create(
            author=self.author_ru, language=self.lang_ru, **book_data)

        url = reverse('api:books-detail', args=[book.pk])

        data = book_data
        data['name'] = 'Власть тьмы'
        data.update({'author': self.author_ru.pk, 'language': self.lang_ru.pk})

        response = self.staff_client.put(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Book.objects.get(pk=book.pk).name, data['name'])

        book.delete()

    def test_staff_can_delete_book(self):
        book = Book.objects.create(
            name='Влаь тьмы', publication_year=1887, author=self.author_ru,
            language=self.lang_ru)

        url = reverse('api:books-detail', args=[book.pk])

        response = self.staff_client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), self.books_count)
        self.assertEqual(Book.objects.filter(pk=book.pk).count(), 0)

        book.delete()

    def test_user_can_read_book(self):
        url = reverse('api:books-detail', args=[self.book_ru.pk])
        response = self.user_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.book_ru.name)

    def test_user_cant_read_book_from_future(self):
        url = reverse('api:books-detail', args=[self.book_ru_from_future.pk])
        response = self.user_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_search_book(self):
        reversed = reverse('api:books-list')

        url = '{}?search={}'.format(reversed, 'толстой,война')

        response = self.user_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        url = '{}?search={}'.format(reversed, 'Толстой')
        response = self.user_client.get(url)

        item = response.data[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            Book.objects.get(pk=item['id']).name, item['name'])

    def test_user_can_list_book(self):
        url = reverse('api:books-list')
        response = self.user_client.get(url)

        item = response.data[1]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.books_count_for_user)
        self.assertEqual(
            Book.objects.get(pk=item['id']).name, item['name'])

    def test_user_cant_create_book(self):
        url = reverse('api:books-list')
        data = {'name': 'Власть тьмы', 'publication_year': 1887,
                'author': self.author_ru.pk, 'language': self.lang_ru.pk}

        response = self.user_client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), self.books_count)

    def test_user_cant_partial_update_book(self):
        book = Book.objects.create(
            name='Влаь тьмы', publication_year=1887, author=self.author_ru,
            language=self.lang_ru)

        url = reverse('api:books-detail', args=[book.pk])
        data = {'name': 'Власть тьмы'}

        response = self.user_client.patch(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Book.objects.get(pk=book.pk).name, data['name'])

        book.delete()

    def test_user_cant_update_book(self):
        book_data = {'name': 'Влаь тьмы', 'publication_year': 1887}

        book = Book.objects.create(
            author=self.author_ru, language=self.lang_ru, **book_data)

        url = reverse('api:books-detail', args=[book.pk])

        data = book_data
        data['name'] = 'Власть тьмы'
        data.update({'author': self.author_ru.pk, 'language': self.lang_ru.pk})

        response = self.user_client.put(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Book.objects.get(pk=book.pk).name, data['name'])

        book.delete()

    def test_user_cant_delete_book(self):
        book = Book.objects.create(
            name='Влаь тьмы', publication_year=1887, author=self.author_ru,
            language=self.lang_ru)

        url = reverse('api:books-detail', args=[book.pk])

        response = self.user_client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), self.books_count + 1)
        self.assertEqual(Book.objects.filter(pk=book.pk).count(), 1)

        book.delete()

    def test_anon_cant_access_author(self):
        url_list = reverse('api:authors-list')
        url_detail = reverse('api:authors-detail', args=[self.author_ru.pk])

        return self.anon_access(url_list, url_detail)

    def test_staff_can_read_author(self):
        url = reverse('api:authors-detail', args=[self.author_ru.pk])
        response = self.staff_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['last_name'], self.author_ru.last_name)

    def test_staff_can_list_author(self):
        url = reverse('api:authors-list')
        response = self.staff_client.get(url)

        item = response.data[1]
        obj = Author.objects.get(pk=item['id'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(obj.last_name, item['last_name'])

    def test_staff_can_create_author(self):
        url = reverse('api:authors-list')

        response = self.staff_client.post(url, data=self.test_author_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), self.authors_count + 1)

        Author.objects.filter(
            last_name=self.test_author_data['last_name']).delete()

    def test_staff_can_partial_update_author(self):
        author = Author.objects.create(**self.test_author_data)

        url = reverse('api:authors-detail', args=[author.pk])
        data = {'middle_name': 'Михалыч'}

        response = self.staff_client.patch(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Author.objects.get(pk=author.pk).middle_name, data['middle_name'])

        author.delete()

    def test_staff_can_update_author(self):
        author = Author.objects.create(**self.test_author_data)

        url = reverse('api:authors-detail', args=[author.pk])
        data = self.test_author_data
        data['middle_name'] = 'Михалыч'

        response = self.staff_client.put(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Author.objects.get(pk=author.pk).middle_name, data['middle_name'])

        author.delete()

    def test_staff_can_delete_author(self):
        author = Author.objects.create(**self.test_author_data)

        url = reverse('api:authors-detail', args=[author.pk])

        response = self.staff_client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Author.objects.count(), self.authors_count)
        self.assertEqual(Author.objects.filter(pk=author.pk).count(), 0)

        author.delete()

    def test_user_can_read_author(self):
        url = reverse('api:authors-detail', args=[self.author_ru.pk])
        response = self.user_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['last_name'], self.author_ru.last_name)

    def test_user_can_list_author(self):
        url = reverse('api:authors-list')
        response = self.user_client.get(url)

        item = response.data[1]
        obj = Author.objects.get(pk=item['id'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(obj.last_name, item['last_name'])

    def test_user_cant_create_author(self):
        url = reverse('api:authors-list')

        response = self.user_client.post(url, data=self.test_author_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Author.objects.count(), self.authors_count)

    def test_user_cant_partial_update_author(self):
        author = Author.objects.create(**self.test_author_data)

        url = reverse('api:authors-detail', args=[author.pk])
        data = {'first_name': 'Петр'}

        response = self.user_client.patch(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Author.objects.get(pk=author.pk).first_name, data['first_name'])

        author.delete()

    def test_user_cant_update_author(self):
        author = Author.objects.create(**self.test_author_data)

        url = reverse('api:authors-detail', args=[author.pk])
        data = {'first_name': 'Петр'}

        response = self.user_client.put(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(
            Author.objects.get(pk=author.pk).first_name, data['first_name'])

        author.delete()

    def test_user_cant_delete_author(self):
        author = Author.objects.create(**self.test_author_data)

        url = reverse('api:authors-detail', args=[author.pk])

        response = self.user_client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Author.objects.count(), self.authors_count + 1)
        self.assertEqual(Author.objects.filter(pk=author.pk).count(), 1)

        author.delete()

    def test_user_can_follow_author(self):
        url = reverse('api:follows-list')

        response = self.user_client.post(url, {'author': self.author_ru.pk})

        following = get_object_or_404(Follow, user=self.user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follow.objects.count(), 1)

        following.delete()

    def test_user_can_list_follows(self):
        f1 = Follow.objects.create(user=self.user, author=self.author_ru)
        f2 = Follow.objects.create(user=self.user, author=self.author_en)
        f3 = Follow.objects.create(user=self.user, author=self.author_fr)

        url = reverse('api:follows-list')

        response = self.user_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        f1.delete()
        f2.delete()
        f3.delete()

    def test_user_can_unfollow_author(self):
        following = Follow.objects.create(
            user=self.user, author=self.author_ru)

        url = reverse('api:follows-detail', args=[following.pk])

        response = self.user_client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Follow.objects.filter(user=self.user).exists())

    def test_user_can_read_following(self):
        following = Follow.objects.create(
            user=self.user, author=self.author_ru)

        url = reverse('api:follows-detail', args=[following.pk])

        response = self.user_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.pk)

        following.delete()

    def test_user_cant_update_following(self):
        following = Follow.objects.create(
            user=self.user, author=self.author_ru)

        url = reverse('api:follows-detail', args=[following.pk])

        response = self.user_client.put(url, {'author': self.author_fr.pk})

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            Follow.objects.get(pk=following.pk).author, self.author_ru)

        following.delete()

    def test_user_cant_partial_update_following(self):
        following = Follow.objects.create(
            user=self.user, author=self.author_ru)

        url = reverse('api:follows-detail', args=[following.pk])

        response = self.user_client.patch(url, {'author': self.author_fr.pk})

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            Follow.objects.get(pk=following.pk).author, self.author_ru)

        following.delete()

    def test_user_cant_unfollow_others_followings(self):
        others_following = Follow.objects.create(
            user=self.staff, author=self.author_en)

        url = reverse('api:follows-detail', args=[others_following.pk])

        response = self.user_client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Follow.objects.filter(pk=others_following.pk).exists())

        others_following.delete()

    def test_email_send_after_book_add(self):
        following = Follow.objects.create(
            user=self.user, author=self.author_en)

        book_name = 'Test book'
        mail_subject = f'Доступна книга "{book_name}" ({self.author_en})'

        book_add_url = reverse('api:books-list')
        book_add_data = {
            'name': book_name,
            'language': self.lang_en.pk,
            'author': self.author_en.pk,
            'publication_year': 2020
        }

        response = self.staff_client.post(book_add_url, book_add_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, mail_subject)

        book_add_data['author'] = self.author_ru.pk
        response = self.staff_client.post(book_add_url, book_add_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)

        following.delete()
