from django.urls import path
from .views import RegisterView, LoginView, ChatView, ChatHistoryView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='auth_register'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('chat-history/', ChatHistoryView.as_view(), name='chat_history'),
]
