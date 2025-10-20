from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'error': 'Request failed',
            'details': response.data,
            'status_code': response.status_code
        }
    else:
        response = Response(
            {
                'error': 'Internal server error',
                'details': str(exc),
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response