from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('api/v1/registration/', views.Register.as_view()),
    path('api/v1/manip/<int:pk>/', views.UserManip.as_view()),
    path('api/v1/auth/', include('djoser.urls')),
    path('api/v1/auth/', include('djoser.urls.authtoken')),
]