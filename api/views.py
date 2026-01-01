from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Welcome to API',
        'endpoints': {
            'materials/courses/': 'Course CRUD',
            'materials/lessons/': 'Lesson CRUD',
        }
    })

@api_view(['GET'])
def hello_api(request):
    return Response({'message': 'Hello from API!'})
