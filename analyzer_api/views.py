from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.urls import get_resolver
from analyzer_api.serializers import StringAnalysisSerializer

from .models import StringAnalysis
from .filters import StringAnalysisFilter
from .services import StringAnalysisService


class StringAnalysisListCreateView(generics.ListCreateAPIView):
    serializer_class = StringAnalysisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StringAnalysisFilter
    
    def get_queryset(self):
        return StringAnalysis.objects.all().order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        filters_applied = {}
        valid_params = ['is_palindrome', 'min_length', 'max_length', 'word_count', 'contains_character']
        
        for param in valid_params:
            value = request.GET.get(param)
            if value is not None:
                if param == 'is_palindrome' and value.lower() in ['true', 'false']:
                    filters_applied[param] = value.lower() == 'true'
                else:
                    filters_applied[param] = value
        return Response({
            "data": response.data,
            "count": len(response.data),
            "filters_applied": filters_applied
        })
    
    def create(self, request, *args, **kwargs):
        value = request.data.get('value')
        
        analysis, error, status_code = StringAnalysisService.create_string_analysis(value)
        
        if error:
            return Response(error, status=status_code)
        
        serializer = self.get_serializer(analysis)
        return Response(serializer.data, status=status_code)


class StringAnalysisRetrieveDeleteView(APIView):
    """
    Combined view for GET and DELETE on /strings/{string_value}/
    """
    
    def get(self, request, string_value, format=None):
        """GET /strings/{string_value} - Get specific string analysis"""
        analysis, error, status_code = StringAnalysisService.get_string_analysis(string_value)
        
        if error:
            return Response(error, status=status_code)
        
        serializer = StringAnalysisSerializer(analysis)
        return Response(serializer.data)
    
    def delete(self, request, string_value, format=None):
        """DELETE /strings/{string_value} - Delete specific string analysis"""
        success, error, status_code = StringAnalysisService.delete_string_analysis(string_value)
        
        if error:
            return Response(error, status=status_code)
        
        return Response(status=status_code)


class NaturalLanguageFilterView(APIView):
    """
    GET /strings/filter-by-natural-language - Filter using natural language
    """
    
    def get(self, request, format=None):
        query = request.GET.get('query', '').strip()
        
        queryset, interpreted_query, error, status_code = StringAnalysisService.get_natural_language_results(query)
        
        if error:
            return Response(error, status=status_code)
        
        serializer = StringAnalysisSerializer(queryset, many=True)
        return Response({
            "data": serializer.data,
            "count": queryset.count(),
            "interpreted_query": interpreted_query
        })


class StringAnalysisBulkView(APIView):
    """
    Additional bulk operations (optional enhancement)
    """
    
    def get(self, request, format=None):
        """GET /strings/bulk - Get multiple analyses by IDs or values"""
        ids = request.GET.getlist('id')
        values = request.GET.getlist('value')
        hashes = request.GET.getlist('hash')
        
        queryset = StringAnalysis.objects.all()
        
        if ids:
            queryset = queryset.filter(id__in=ids)
        if values:
            queryset = queryset.filter(value__in=values)
        if hashes:
            queryset = queryset.filter(sha256_hash__in=hashes)
        
        serializer = StringAnalysisSerializer(queryset, many=True)
        return Response({
            "data": serializer.data,
            "count": queryset.count()
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
        
class URLDebugView(APIView):
    def get(self, request):
        resolver = get_resolver()
        url_list = []
        
        def extract_patterns(patterns, prefix=''):
            for pattern in patterns:
                if hasattr(pattern, 'pattern'):
                    url_list.append(f"{prefix}{pattern.pattern}")
                if hasattr(pattern, 'url_patterns'):
                    extract_patterns(pattern.url_patterns, f"{prefix}{pattern.pattern}")
        
        extract_patterns(resolver.url_patterns)
        return Response({
            "registered_urls": url_list,
            "requested_path": request.path,
            "app_name": "analyzer_api"
        })