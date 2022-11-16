from django.urls import path
from . import views

urlpatterns = [
    path('registeruser/', views.registerUser, name='registeruser'),
    path('registervendor/', views.registerVendor, name='registervendor'),
]