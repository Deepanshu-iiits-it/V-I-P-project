from register import views
from django.urls import path, include
urlpatterns = [
    path('', views.register, name='register'),
]
