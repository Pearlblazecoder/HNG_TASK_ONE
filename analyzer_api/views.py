from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import StringAnalysis
from .serializers import StringAnalysisSerializer
from .filters import StringAnalysisFilter
from .services import StringAnalysisService


class StringAnalysisListCreateView(generics.ListCreateAPIView):
    serializer_class = StringAnalysisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StringAnalysisFilter
    
    def get_queryset(self):
        return StringAnalysis.objects.all().order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        filters_applied = {}
        valid_params = ['is_palindrome', 'min_length', 'max_length', 'word_count', 'contains_character']
        
        for param in valid_params:
            value = request.GET.get(param)
            if value is not None:
                if param == 'is_palindrome' and value.lower() in ['true', 'false']:
                    filters_applied[param] = value.lower() == 'true'
                else:
                    filters_applied[param] = value
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "data": serializer.data,
            "count": queryset.count(),
            "filters_applied": filters_applied
        })
    
    def create(self, request, *args, **kwargs):
        if 'value' not in request.data:
            return Response(
                {"error": "Missing 'value' field"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(request.data.get('value'), str):
            return Response(
                {"error": "Value must be a string"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        value = request.data.get('value')
        analysis, error, status_code = StringAnalysisService.create_string_analysis(value)
        
        if error:
            return Response(error, status=status_code)
        
        serializer = self.get_serializer(analysis)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StringAnalysisRetrieveDeleteView(APIView):
    """
    GET /strings/{string_value} - Get specific string analysis
    DELETE /strings/{string_value} - Delete specific string analysis
    """
    
    def get(self, request, string_value, format=None):
        analysis, error, status_code = StringAnalysisService.get_string_analysis(string_value)
        
        if error:
            return Response(error, status=status_code)
        
        serializer = StringAnalysisSerializer(analysis)
        return Response(serializer.data)
    
    def delete(self, request, string_value, format=None):
        success, error, status_code = StringAnalysisService.delete_string_analysis(string_value)
        
        if error:
            return Response(error, status=status_code)
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class NaturalLanguageFilterView(APIView):
    """
    GET /strings/filter-by-natural-language - Filter using natural language
    """
    
    def get(self, request, format=None):
        query = request.GET.get('query', '').strip()
        
        if not query:
            return Response(
                {"error": "Query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset, interpreted_query, error, status_code = StringAnalysisService.get_natural_language_results(query)
        
        if error:
            return Response(error, status=status_code)
        
        serializer = StringAnalysisSerializer(queryset, many=True)
        return Response({
            "data": serializer.data,
            "count": queryset.count(),
            "interpreted_query": interpreted_query
        })


class HealthCheckView(APIView):
    """
    Health check endpoint
    """
    
    def get(self, request, format=None):
        return Response({
            "status": "healthy",
            "total_analyses": StringAnalysis.objects.count(),
            "service": "String Analyzer API",
            "version": "1.0.0"
        })