from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Triggers a background task to send a welcome email upon successful creation.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        """
        Save the user and schedule the welcome email task.
        """
        user = serializer.save()
        from .tasks import send_welcome_email, scheduler
        from django.utils import timezone
        scheduler.add_job(send_welcome_email, 'date', run_date=timezone.now(), args=[user.email])

class LoginView(TokenObtainPairView):
    """
    API endpoint for user login.
    Returns JWT access and refresh tokens.
    """
    permission_classes = (AllowAny,)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from .rag_service import retrieve_context, get_rag_response

class ChatView(APIView):
    """
    API endpoint for interacting with the chatbot.
    Handles message persistence, context retrieval (RAG), and AI response generation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('message')
        if not query:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Save user message to database
        ChatMessage.objects.create(user=request.user, role='user', content=query)

        try:
            # Retrieve recent chat history (e.g., last 5 messages) to provide context to the LLM
            recent_history = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:5]
            # Reverse to chronological order for the prompt
            recent_history = reversed(recent_history)

            # Retrieve relevant documents from Pinecone
            context = retrieve_context(query)
            
            # Generate response using Mistral AI
            response_obj = get_rag_response(query, context, chat_history=recent_history)
            
            bot_response = response_obj
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save bot response to database
        ChatMessage.objects.create(user=request.user, role='bot', content=bot_response)

        return Response({"response": bot_response})

class ChatHistoryView(generics.ListAPIView):
    """
    API endpoint to retrieve the chat history for the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user).order_by('timestamp')
