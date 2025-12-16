from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model extending AbstractUser.
    Uses 'email' as the unique identifier for authentication instead of 'username'.
    """
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class ChatMessage(models.Model):
    """
    Model to store chat history between the user and the bot.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} message by {self.user.email} at {self.timestamp}"

class Document(models.Model):
    """
    Model to store documents that can be used for RAG context.
    (Note: Actual vector embeddings are stored in Pinecone, this is for metadata/admin reference)
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
