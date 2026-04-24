from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Author, Book, BorrowRecord


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'birth_date', 'biography']


class BookSerializer(serializers.ModelSerializer):
    author_detail = AuthorSerializer(source='author', read_only=True)  # вложенный автор только для чтения

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'author_detail',
            'genre', 'publication_year', 'isbn', 'available_copies'
        ]
        extra_kwargs = {
            'author': {'write_only': True}  # при создании/обновлении передаём только id автора
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']


class BorrowRecordSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = BorrowRecord
        fields = [
            'id', 'user', 'user_detail', 'book', 'book_title',
            'borrowed_at', 'due_date', 'returned_at'
        ]
        extra_kwargs = {
            'user': {'write_only': True},  # при создании передаём id пользователя
            'book': {'write_only': True}
        }

    def validate_book(self, value):
        """Проверка, что есть доступные экземпляры."""
        if value.available_copies < 1:
            raise serializers.ValidationError("Нет доступных экземпляров.")
        return value

    def create(self, validated_data):
        book = validated_data['book']
        book.available_copies -= 1
        book.save()
        return super().create(validated_data)
