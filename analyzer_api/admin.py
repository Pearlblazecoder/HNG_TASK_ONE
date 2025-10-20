from django.contrib import admin
from .models import StringAnalysis


class StringAnalysisAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for StringAnalysis model
    """
    list_display = (
        'truncated_value', 
        'length', 
        'is_palindrome', 
        'word_count', 
        'unique_char_count',
        'created_at'
    )
    
    list_filter = (
        'is_palindrome',
        'length',
        'word_count',
        'created_at',
    )
    
    search_fields = (
        'value',
        'sha256_hash',
    )
    
    readonly_fields = (
        'length',
        'is_palindrome',
        'word_count',
        'unique_char_count',
        'character_frequency',
        'sha256_hash',
        'created_at',
        'updated_at',
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('value', 'sha256_hash')
        }),
        ('Analysis Results', {
            'fields': (
                'length',
                'is_palindrome', 
                'word_count',
                'unique_char_count',
                'character_frequency',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    
    def truncated_value(self, obj):
        """
        Display truncated string value in list view
        """
        if len(obj.value) > 50:
            return f"{obj.value[:47]}..."
        return obj.value
    truncated_value.short_description = 'String Value'
    
    def has_add_permission(self, request):
        """
        Disable adding via admin - should only be created via API
        """
        return False
    
    def has_change_permission(self, request, obj=None):
        """
        Disable editing via admin - analysis is computed automatically
        """
        return False


admin.site.register(StringAnalysis, StringAnalysisAdmin)