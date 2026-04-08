"""
Health check endpoint.
Returns 200 if the application is alive and DB is reachable.
Used by Docker HEALTHCHECK and load balancers.
"""
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone


def health_check(request):
    """GET /health/ — liveness + readiness probe."""
    checks = {'status': 'ok', 'timestamp': timezone.now().isoformat()}

    # Database check
    try:
        connection.ensure_connection()
        checks['database'] = 'ok'
    except Exception as e:
        checks['database'] = f'error: {str(e)}'
        checks['status'] = 'degraded'

    status_code = 200 if checks['status'] == 'ok' else 503
    return JsonResponse(checks, status=status_code)
