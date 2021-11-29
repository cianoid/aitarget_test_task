from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Author(models.Model):
    last_name = models.CharField('Фамилия', max_length=150)
    first_name = models.CharField('Имя', max_length=150)
    middle_name = models.CharField('Отчество', max_length=150, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'


class Language(models.Model):
    name = models.CharField('Язык', max_length=50)

    def __str__(self):
        return self.name


class Book(models.Model):
    author = models.ForeignKey(
        Author, verbose_name='Автор книги', on_delete=models.CASCADE,
        related_name='books')
    language = models.ForeignKey(
        Language, verbose_name='Язык книги', on_delete=models.PROTECT,
        related_name='books')
    name = models.CharField('Название книги', max_length=500)
    publication_year = models.PositiveSmallIntegerField('Год публикации')

    def __str__(self):
        return f'{self.name}, {self.publication_year}'


class Follow(models.Model):
    user = models.ForeignKey(
        User, related_name='followings', on_delete=models.CASCADE,
        verbose_name='Подписчик')
    author = models.ForeignKey(
        Author, related_name='followers', on_delete=models.CASCADE,
        verbose_name='Автор')

    class Meta:
        unique_together = ('user', 'author')
