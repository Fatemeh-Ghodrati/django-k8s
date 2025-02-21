from django.urls import path
from . import views

urlpatterns = [
    path('users/new_user/', views.USerCreateView.as_view(), name='user-create'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
]
