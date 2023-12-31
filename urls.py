from . import views
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('unencrypt/', views.unencrypt_view, name='unencrypt'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
