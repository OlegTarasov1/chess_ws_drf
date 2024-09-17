from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.index),
    path('chat_test/', views.chat_test, name = 'chat_test')
]