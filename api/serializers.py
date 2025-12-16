from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Handles user registration and password hashing.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')

    def create(self, validated_data):
        """
        Create a new user with a hashed password.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for ChatMessage model.
    Used for retrieving chat history.
    """
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'timestamp']
