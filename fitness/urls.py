from django.urls import path
from . import views

urlpatterns = [
    path('', views.onboarding, name='onboarding'),
    path('update/', views.update_data, name='update_data'),
    path('history/', views.history, name='history'),
]