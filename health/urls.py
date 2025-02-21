from django.urls import path
from .views import liveness, readiness

urlpatterns = [
    path("liveness/", liveness, name="liveness"),
    path("readiness/", readiness, name="readiness"),
]
