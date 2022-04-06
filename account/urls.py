from django.urls import path
from account import views

urlpatterns = [
    path('', views.signup_view, name='signup'),
]
