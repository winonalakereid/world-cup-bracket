from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('groups', views.index, name='groups'),
    path('matches', views.matches, name='matches'),
    path('knockout', views.knockout, name='knockout')
]