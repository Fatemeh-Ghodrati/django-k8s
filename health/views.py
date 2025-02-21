from django.http import JsonResponse
from django.db import connection

def liveness(request):
    """Liveness probe: If Django is running, return success."""
    return JsonResponse({"status": "ok"})

def readiness(request):
    """Readiness probe: Check database connection."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1") 
        return JsonResponse({"status": "ready"})
    except Exception as e:
        return JsonResponse({"status": "unready", "error": str(e)}, status=500)
