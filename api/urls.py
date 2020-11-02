from django.urls import path
from api import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/v1/weather/', views.api_view, name='api')
]
