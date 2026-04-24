import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Название содержит')
    author = django_filters.CharFilter(field_name='author__last_name', lookup_expr='icontains', label='Фамилия автора')
    genre = django_filters.ChoiceFilter(choices=Book.GENRE_CHOICES, label='Жанр')
    publication_year = django_filters.NumberFilter(label='Год издания')

    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'publication_year']
