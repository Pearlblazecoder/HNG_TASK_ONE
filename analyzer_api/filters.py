import django_filters
from .models import StringAnalysis

class StringAnalysisFilter(django_filters.FilterSet):
    min_length = django_filters.NumberFilter(field_name='length', lookup_expr='gte')
    max_length = django_filters.NumberFilter(field_name='length', lookup_expr='lte')
    is_palindrome = django_filters.BooleanFilter(field_name='is_palindrome')
    word_count = django_filters.NumberFilter(field_name='word_count')
    contains_character = django_filters.CharFilter(method='filter_contains_character')
    
    class Meta:
        model = StringAnalysis
        fields = ['is_palindrome', 'word_count']
    
    def filter_contains_character(self, queryset, name, value):
        """
        Filter strings that contain a specific character
        Value must be a single character
        """
        if not value:
            return queryset
            
        if len(value) != 1:
            raise ValueError("contains_character must be a single character")
        
        return queryset.filter(value__icontains=value)