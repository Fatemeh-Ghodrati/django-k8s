import logging
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserSerializer, UserSummarySerializer
from rest_framework.response import Response
from django.http import JsonResponse
from .models import User
from prometheus_client import Counter, Gauge
import psutil
from django.db import connections

REQUEST_200_COUNT = Counter('http_200_responses_total', 'Total number of successful (200) responses')
REQUEST_404_COUNT = Counter('http_404_responses_total', 'Total number of not found (404) responses')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('memory_usage_percent', 'Memory usage percentage')

logger = logging.getLogger('users')

class LivenessProbeView(APIView):
    def get(self, request):
        return JsonResponse({"status": "alive"}, status=200)
    

class ReadinessProbeView(APIView):
    def get(self, request):
        try:
            connections["default"].cursor()
        except Exception as e:
            return JsonResponse({"status": "unready", "error": str(e)}, status=503)

        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=1)

        if memory_usage > 90 or cpu_usage > 90:
            return JsonResponse({"status": "unready", "cpu": cpu_usage, "memory": memory_usage}, status=503)

        return JsonResponse({"status": "ready"}, status=200)

class USerCreateView(APIView):
    def post(self, request):
        logger.info("Trying to create a new user")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.debug(f"User created successfully: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"User creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UserDetailView(APIView):
    def get_object(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            REQUEST_404_COUNT.inc()
            logger.error(f"User with id {user_id} not found")
            return None
        
    def get(self, request, user_id):
        logger.info(f"Fetching details for user ID {user_id}")
        user = self.get_object(user_id)
        if user is None:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        REQUEST_200_COUNT.inc()
        serializer = UserSummarySerializer(user)
        logger.debug(f"User details retrieved: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    
def get_memory_usage():
    process = psutil.Process()
    return process.memory_info().rss

def get_cpu_usage():
    process = psutil.Process()
    return process.cpu_percent(interval=1.0)

MEMORY_USAGE.set(get_memory_usage())
CPU_USAGE.set(get_cpu_usage())