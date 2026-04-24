from django.contrib.auth.models import User
from django.db import models


class Author(models.Model):
    """Автор книги."""
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    biography = models.TextField(blank=True, verbose_name="Биография")

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Book(models.Model):
    """Книга в библиотеке."""
    GENRE_CHOICES = [
        ('fiction', 'Художественная литература'),
        ('non-fiction', 'Нон-фикшн'),
        ('science', 'Наука'),
        ('history', 'История'),
        ('fantasy', 'Фэнтези'),
        ('biography', 'Биография'),
        ('other', 'Другое'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название")
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name="Автор"
    )
    genre = models.CharField(
        max_length=20,
        choices=GENRE_CHOICES,
        default='other',
        verbose_name="Жанр"
    )
    publication_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Год издания")
    isbn = models.CharField(max_length=20, unique=True, verbose_name="ISBN")
    available_copies = models.PositiveIntegerField(default=1, verbose_name="Доступно экземпляров")

    class Meta:
        ordering = ['title']
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return self.title


class BorrowRecord(models.Model):
    """Запись о выдаче книги читателю."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='borrow_records',
        verbose_name="Пользователь"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='borrow_records',
        verbose_name="Книга"
    )
    borrowed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата выдачи")
    due_date = models.DateField(verbose_name="Вернуть до")
    returned_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата возврата")

    class Meta:
        verbose_name = "Запись выдачи"
        verbose_name_plural = "Записи выдач"
        ordering = ['-borrowed_at']

    def __str__(self):
        return f"{self.user} взял '{self.book}'"
