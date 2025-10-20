from django.db import models
import hashlib
import json

class StringAnalysis(models.Model):
    value = models.TextField(unique=True)
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    word_count = models.IntegerField()
    unique_char_count = models.IntegerField()
    character_frequency = models.JSONField()
    sha256_hash = models.CharField(max_length=64, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "String Analyses"
    
    def __str__(self):
        return f"{self.value[:50]}..." if len(self.value) > 50 else self.value
    
    def save(self, *args, **kwargs):
        self.length = len(self.value)
        self.is_palindrome = self._check_palindrome()
        self.word_count = self._count_words()
        self.unique_char_count = self._count_unique_chars()
        self.character_frequency = self._calculate_char_frequency()
        self.sha256_hash = self._calculate_sha256()
        
        super().save(*args, **kwargs)
    
    def _check_palindrome(self):
        cleaned = ''.join(char.lower() for char in self.value if char.isalnum())
        return cleaned == cleaned[::-1]
    
    def _count_words(self):
        return len(self.value.split())
    
    def _count_unique_chars(self):
        return len(set(self.value))
    
    def _calculate_char_frequency(self):
        freq = {}
        for char in self.value:
            freq[char] = freq.get(char, 0) + 1
        return freq
    
    def _calculate_sha256(self):
        return hashlib.sha256(self.value.encode('utf-8')).hexdigest()
    
    def to_dict(self):
        return {
            'value': self.value,
            'length': self.length,
            'is_palindrome': self.is_palindrome,
            'word_count': self.word_count,
            'unique_char_count': self.unique_char_count,
            'character_frequency': self.character_frequency,
            'sha256_hash': self.sha256_hash,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }