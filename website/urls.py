from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('team/', views.team, name='team'),
    path('story/', views.story, name='story'),
    path('contact/', views.contact, name='contact'),
]
