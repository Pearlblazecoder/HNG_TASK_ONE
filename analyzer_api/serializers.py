from rest_framework import serializers
from .models import StringAnalysis

class StringInputSerializer(serializers.Serializer):
    value = serializers.CharField(required=True, allow_blank=False, trim_whitespace=False)
    
    def validate_value(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Value must be a string")
        return value

class StringAnalysisSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='sha256_hash', read_only=True)
    properties = serializers.SerializerMethodField()
    
    class Meta:
        model = StringAnalysis
        fields = [
            'id', 'value', 'properties', 'created_at'
        ]
        read_only_fields = ['id', 'properties', 'created_at']
    
    def get_properties(self, obj):
        return {
            'length': obj.length,
            'is_palindrome': obj.is_palindrome,
            'unique_characters': obj.unique_char_count,
            'word_count': obj.word_count,
            'sha256_hash': obj.sha256_hash,
            'character_frequency_map': obj.character_frequency
        }