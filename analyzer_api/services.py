from django.db import IntegrityError
from .models import StringAnalysis

class StringAnalysisService:
    
    @staticmethod
    def create_string_analysis(value):
        """
        Create a new string analysis
        Returns: (analysis_object, error_message, status_code)
        """
        if value is None:
            return None, {"error": "Missing 'value' field"}, 400
        if not isinstance(value, str):
            return None, {"error": "Value must be a string"}, 422
        if StringAnalysis.objects.filter(value=value).exists():
            return None, {"error": "String already exists"}, 409
        
        try:
            analysis = StringAnalysis(value=value)
            analysis.save()
            return analysis, None, 201
            
        except Exception as e:
            return None, {"error": "Failed to process string", "details": str(e)}, 422
    
    @staticmethod
    def get_string_analysis(identifier):
        """
        Get string analysis by value or hash
        Returns: (analysis_object, error_message, status_code)
        """
        try:
            analysis = StringAnalysisService._find_analysis(identifier)
            return analysis, None, 200
        except StringAnalysis.DoesNotExist:
            return None, {"error": "String analysis not found"}, 404
    
    @staticmethod
    def delete_string_analysis(identifier):
        """
        Delete string analysis by value or hash
        Returns: (success, error_message, status_code)
        """
        try:
            analysis = StringAnalysisService._find_analysis(identifier)
            analysis.delete()
            return True, None, 204
        except StringAnalysis.DoesNotExist:
            return False, {"error": "String analysis not found"}, 404
    
    @staticmethod
    def _find_analysis(identifier):
        """Helper method to find analysis by value or hash"""
        try:
            return StringAnalysis.objects.get(value=identifier)
        except StringAnalysis.DoesNotExist:
            if len(identifier) == 64 and all(c in '0123456789abcdef' for c in identifier.lower()):
                return StringAnalysis.objects.get(sha256_hash=identifier)
            raise StringAnalysis.DoesNotExist("String analysis not found")
    
    @staticmethod
    def get_filtered_analyses(filters):
        """
        Get filtered analyses based on query parameters
        Returns: (queryset, error_message, status_code)
        """
        try:
            queryset = StringAnalysis.objects.all().order_by('-created_at')
            
            # Apply standard filters
            from .filters import StringAnalysisFilter
            filterset = StringAnalysisFilter(filters, queryset=queryset)
            if not filterset.is_valid():
                return None, {"error": "Invalid filters", "details": filterset.errors}, 400
            
            return filterset.qs, None, 200
            
        except ValueError as e:
            return None, {"error": "Invalid query parameter values", "details": str(e)}, 400
        except Exception as e:
            return None, {"error": "Invalid query parameters", "details": str(e)}, 400
    
    @staticmethod
    def get_natural_language_results(query):
        """
        Get analyses based on natural language query
        Returns: (queryset, interpreted_query, error_message, status_code)
        """
        if not query.strip():
            return None, None, {"error": "Query parameter is required"}, 400
        
        try:
            from .natural_language_parser import NaturalLanguageQueryParser
            filters, parsed_filters = NaturalLanguageQueryParser.parse(query)
            queryset = StringAnalysis.objects.filter(filters).order_by('-created_at')
            interpreted_query = {
                "original": query,
                "parsed_filters": parsed_filters
            }
            
            return queryset, interpreted_query, None, 200
            
        except ValueError as e:
            return None, None, {"error": "Unable to parse natural language query", "details": str(e)}, 400
        except Exception as e:
            return None, None, {"error": "Query parsed but resulted in conflicting filters", "details": str(e)}, 422