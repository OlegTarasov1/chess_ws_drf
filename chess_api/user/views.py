from django.shortcuts import render
from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegistrationSerializer
from .permissions import UserManipPermission


class UserManip(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserManipPermission, )


class Register(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserRegistrationSerializer