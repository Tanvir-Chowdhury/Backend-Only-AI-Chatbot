from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        from .tasks import send_welcome_email
        send_welcome_email(user.email)

class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from .rag_service import retrieve_context, get_rag_response

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('message')
        if not query:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        ChatMessage.objects.create(user=request.user, role='user', content=query)

        try:
            context = retrieve_context(query)
            response_obj = get_rag_response(query, context)
            
            bot_response = response_obj
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        ChatMessage.objects.create(user=request.user, role='bot', content=bot_response)

        return Response({"response": bot_response})

class ChatHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user).order_by('timestamp')
