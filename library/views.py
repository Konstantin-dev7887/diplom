from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Author, Book, BorrowRecord
from .serializers import (
    AuthorSerializer, BookSerializer,
    UserRegistrationSerializer, UserSerializer,
    BorrowRecordSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .filters import BookFilter


class AuthorViewSet(viewsets.ModelViewSet):
    """Авторы: полный CRUD. Изменять может только администратор."""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]


class BookViewSet(viewsets.ModelViewSet):
    """Книги: CRUD + фильтрация и поиск."""
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = BookFilter
    search_fields = ['title', 'author__first_name', 'author__last_name', 'genre']


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация нового пользователя. Доступна всем."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveAPIView):
    """Профиль текущего пользователя."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class BorrowRecordViewSet(viewsets.ModelViewSet):
    """
    Записи выдачи:
    - Админы видят все записи, пользователи – только свои.
    - Создавать может любой авторизованный (запись на себя), админ – на любого.
    - Закрывать выдачу (возврат) – только админ.
    """
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return BorrowRecord.objects.select_related('user', 'book').all()
        return BorrowRecord.objects.filter(user=user).select_related('book')

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def return_book(self, request, pk=None):
        """Отметить книгу возвращённой (только админ)."""
        record = self.get_object()
        if record.returned_at is not None:
            return Response(
                {'detail': 'Книга уже возвращена.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from django.utils import timezone
        record.returned_at = timezone.now()
        record.save()
        # Увеличиваем счётчик доступных книг
        book = record.book
        book.available_copies += 1
        book.save()
        return Response(self.get_serializer(record).data)
