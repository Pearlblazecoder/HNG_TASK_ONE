from django.db import IntegrityError
from .models import StringAnalysis
from .serializers import StringInputSerializer

class StringAnalysisService:
    """
    Service class to handle string analysis business logic
    """
    
    @staticmethod
    def create_string_analysis(value):
        """
        Create a new string analysis
        Returns: (analysis_object, error_message, status_code)
        """
        input_serializer = StringInputSerializer(data={'value': value})
        if not input_serializer.is_valid():
            return None, {"error": "Invalid input", "details": input_serializer.errors}, 400
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
    
    @staticmethod
    def _get_parsed_filters_description(filters, original_query):
        """Convert Django Q filters to readable description"""
        description = {}
        query_lower = original_query.lower()
        if 'palindrome' in query_lower or 'palindromic' in query_lower:
            if any(word in query_lower for word in ['not', 'non', 'no ']):
                description['is_palindrome'] = False
            else:
                description['is_palindrome'] = True
        if 'longer' in query_lower or 'greater' in query_lower or 'more than' in query_lower:
            import re
            length_match = re.search(r'(\d+)', query_lower)
            if length_match:
                description['min_length'] = int(length_match.group(1)) + 1
        
        if 'shorter' in query_lower or 'less than' in query_lower:
            import re
            length_match = re.search(r'(\d+)', query_lower)
            if length_match:
                description['max_length'] = int(length_match.group(1)) - 1
        if 'single word' in query_lower or 'one word' in query_lower:
            description['word_count'] = 1
        
        if 'multiple words' in query_lower or 'multi word' in query_lower:
            description['word_count__gt'] = 1
        import re
        char_match = re.search(r'containing\s+[\'"]?([a-zA-Z])[\'"]?', query_lower)
        if char_match:
            description['contains_character'] = char_match.group(1)
        
        char_match = re.search(r'with\s+[\'"]?([a-zA-Z])[\'"]?', query_lower)
        if char_match:
            description['contains_character'] = char_match.group(1)
        if not description:
            description['note'] = 'Complex natural language query applied'
            
        return description