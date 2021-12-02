from datetime import datetime

from rest_framework import status
from rest_framework.reverse import reverse
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase, APIClient

from django.contrib.auth import get_user_model

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
        url = reverse('api:books-detail', args=[self.book_ru.pk])
        response = self.staff_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.book_ru.name)

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
