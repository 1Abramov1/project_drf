from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('hello/', views.hello_api, name='hello-api'),
]