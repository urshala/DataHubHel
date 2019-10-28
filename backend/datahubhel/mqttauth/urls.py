from django.urls import path

from . import views

app_name = 'datahubhel.mqttauth'
urlpatterns = [
    path('auth/', views.auth, name='auth'),
    path('superuser/', views.superuser, name='superuser'),
    path('acl/', views.acl, name='acl'),
]
