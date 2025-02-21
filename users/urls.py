from django.urls import path
from . import views

urlpatterns = [
    path('users/new_user/', views.USerCreateView.as_view(), name='user-create'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
    path('liveness/', views.LivenessProbeView.as_view(), name='liveness_probe'),
    path('readiness/', views.ReadinessProbeView.as_view(), name='readiness_probe'),
]
